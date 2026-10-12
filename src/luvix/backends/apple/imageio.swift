import Foundation
import CoreGraphics
import CoreImage
import ImageIO
import UniformTypeIdentifiers

func die(_ message: String) -> Never { fputs("\(message)\n", stderr); exit(1) }
func source(_ url: URL) -> CGImageSource {
    guard let s = CGImageSourceCreateWithURL(url as CFURL, nil) else { die("Cannot open \(url.path)") }
    return s
}
func auxiliary(_ s: CGImageSource) -> [String: Any] {
    guard let d = CGImageSourceCopyAuxiliaryDataInfoAtIndex(s, 0, kCGImageAuxiliaryDataTypeHDRGainMap) as? [String: Any] else { die("Missing HDR gain map") }
    return d
}
struct MapInfo { let width: Int; let height: Int; let stride: Int; let bytes: Data }
func mapInfo(_ aux: [String: Any]) -> MapInfo {
    guard let desc = aux[kCGImageAuxiliaryDataInfoDataDescription as String] as? [String: Any],
          let w = desc["Width"] as? Int, let h = desc["Height"] as? Int,
          let stride = desc["BytesPerRow"] as? Int,
          let format = desc["PixelFormat"] as? Int,
          let bytes = aux[kCGImageAuxiliaryDataInfoData as String] as? Data,
          format == 1278226488, w > 0, h > 0, stride >= w, bytes.count == stride*h else {
        die("Expected Apple L008 grayscale gain map; unsupported layout")
    }
    return MapInfo(width: w, height: h, stride: stride, bytes: bytes)
}
func grayImage(_ m: MapInfo) -> CGImage {
    guard let provider = CGDataProvider(data: m.bytes as CFData),
          let img = CGImage(width: m.width, height: m.height, bitsPerComponent: 8,
                            bitsPerPixel: 8, bytesPerRow: m.stride,
                            space: CGColorSpaceCreateDeviceGray(),
                            bitmapInfo: CGBitmapInfo(rawValue: 0), provider: provider,
                            decode: nil, shouldInterpolate: false, intent: .defaultIntent) else { die("Could not decode gain map") }
    return img
}
func writePNG(_ image: CGImage, _ url: URL) {
    guard let d = CGImageDestinationCreateWithURL(url as CFURL, UTType.png.identifier as CFString, 1, nil) else { die("Cannot create PNG") }
    CGImageDestinationAddImage(d, image, nil)
    guard CGImageDestinationFinalize(d) else { die("Could not write PNG") }
}

func sourceOrientation(_ s: CGImageSource) -> Int {
    let props = CGImageSourceCopyPropertiesAtIndex(s, 0, nil) as? [String: Any] ?? [:]
    let orientation = props[kCGImagePropertyOrientation as String] as? Int ?? 1
    guard (1...8).contains(orientation) else { die("Unsupported EXIF orientation \(orientation)") }
    return orientation
}
func inverseOrientation(_ orientation: Int) -> Int {
    switch orientation {
    case 6: return 8
    case 8: return 6
    default: return orientation
    }
}
func editingDimensions(width: Int, height: Int, orientation: Int) -> (Int, Int) {
    switch orientation {
    case 5, 6, 7, 8: return (height, width)
    default: return (width, height)
    }
}
func orientedImage(_ image: CGImage, orientation: Int, grayscale: Bool = false) -> CGImage {
    guard orientation != 1 else { return image }
    let input = CIImage(cgImage: image)
    let transformed = input.oriented(forExifOrientation: Int32(orientation))
    let context = CIContext(options: [.cacheIntermediates: false])
    let colorSpace = grayscale ? CGColorSpaceCreateDeviceGray() : (image.colorSpace ?? CGColorSpaceCreateDeviceRGB())
    let format: CIFormat = grayscale ? .L8 : .RGBA8
    guard let output = context.createCGImage(
        transformed,
        from: transformed.extent,
        format: format,
        colorSpace: colorSpace
    ) else { die("Could not apply EXIF orientation \(orientation)") }
    return output
}
func readEditedMap(_ url: URL, original: MapInfo, orientation: Int) -> Data {
    let s = source(url)
    guard let edited = CGImageSourceCreateImageAtIndex(s, 0, nil) else { die("Invalid edited gain map") }
    let expected = editingDimensions(width: original.width, height: original.height, orientation: orientation)
    guard edited.width == expected.0, edited.height == expected.1 else {
        die("Edited gain map must have dimensions \(expected.0)x\(expected.1)")
    }
    let image = orientedImage(edited, orientation: inverseOrientation(orientation), grayscale: true)
    guard image.width == original.width, image.height == original.height else {
        die("Edited gain map orientation transform produced incompatible dimensions")
    }
    var bytes = [UInt8](original.bytes)
    let success = bytes.withUnsafeMutableBytes { buffer -> Bool in
        guard let ctx = CGContext(data: buffer.baseAddress, width: original.width,
                                  height: original.height, bitsPerComponent: 8,
                                  bytesPerRow: original.stride,
                                  space: CGColorSpaceCreateDeviceGray(),
                                  bitmapInfo: CGImageAlphaInfo.none.rawValue) else { return false }
        ctx.interpolationQuality = .none
        ctx.draw(image, in: CGRect(x: 0, y: 0, width: original.width, height: original.height))
        return true
    }
    guard success else { die("Failed rendering edited gain map") }
    return Data(bytes)
}
func destinationType(_ original: CGImageSource, _ url: URL) -> String {
    guard let sourceType = CGImageSourceGetType(original) as String? else {
        die("Cannot determine source container type")
    }
    let ext = url.pathExtension.lowercased()
    if sourceType == UTType.heic.identifier {
        guard ext == "heic" else { die("HEIC source requires a .heic output filename") }
    } else if sourceType == UTType.jpeg.identifier {
        guard ext == "jpg" || ext == "jpeg" else {
            die("JPEG source requires a .jpg or .jpeg output filename")
        }
    } else {
        die("Unsupported gain-map source container: \(sourceType)")
    }
    return sourceType
}
func writeGainMapImage(_ base: CGImage, _ original: CGImageSource,
                       _ aux: [String: Any], _ url: URL) {
    let format = destinationType(original, url)
    guard let d = CGImageDestinationCreateWithURL(url as CFURL, format as CFString, 1, nil) else {
        die("Cannot create destination for \(format)")
    }
    let props = CGImageSourceCopyPropertiesAtIndex(original, 0, nil)
    CGImageDestinationAddImage(d, base, props)
    CGImageDestinationAddAuxiliaryDataInfo(d, kCGImageAuxiliaryDataTypeHDRGainMap, aux as CFDictionary)
    guard CGImageDestinationFinalize(d) else { die("Could not finalize gain-map image") }
    let check = source(url)
    guard (CGImageSourceGetType(check) as String?) == format else {
        die("Rebuilt container type differs from source")
    }
    _ = mapInfo(auxiliary(check))
    let p = Process(); p.executableURL = URL(fileURLWithPath: "/usr/bin/chflags")
    p.arguments = ["nohidden", url.path]
    do { try p.run(); p.waitUntilExit() } catch { die("chflags failed: \(error)") }
    guard p.terminationStatus == 0 else { die("Could not clear hidden flag") }
}

func details(_ s: CGImageSource) -> [String: Any] {
    let image = CGImageSourceCreateImageAtIndex(s, 0, nil)!
    let m = mapInfo(auxiliary(s))
    let props = CGImageSourceCopyPropertiesAtIndex(s, 0, nil) as? [String: Any] ?? [:]
    let meta = auxiliary(s)[kCGImageAuxiliaryDataInfoMetadata as String]
    return ["base_width": image.width, "base_height": image.height,
            "gain_width": m.width, "gain_height": m.height,
            "gain_stride": m.stride, "gain_format": "L008",
            "color_space": image.colorSpace?.name as String? ?? "unknown",
            "orientation": props[kCGImagePropertyOrientation as String] ?? 1,
            "has_gainmap_metadata": meta != nil]
}
func emitJSON(_ d: [String: Any]) {
    guard let data = try? JSONSerialization.data(withJSONObject: d, options: [.sortedKeys]),
          let text = String(data: data, encoding: .utf8) else { die("JSON error") }
    print(text)
}
let args = CommandLine.arguments
if args.count < 2 { die("Usage: apple_backend inspect|extract|rebuild|validate ...") }
switch args[1] {
case "inspect":
    guard args.count == 3 else { die("inspect source.HEIC|JPG") }
    emitJSON(details(source(URL(fileURLWithPath: args[2]))))
case "extract":
    guard args.count == 4 else { die("extract source.HEIC|JPG directory") }
    let input = URL(fileURLWithPath: args[2]); let s = source(input)
    let dir = URL(fileURLWithPath: args[3], isDirectory: true)
    do { try FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true) } catch { die("Cannot create directory") }
    for name in ["base.png", "gainmap.png", "manifest.json"] {
        guard !FileManager.default.fileExists(atPath: dir.appendingPathComponent(name).path) else { die("Refusing to overwrite " + name) }
    }
    let orientation = sourceOrientation(s)
    let rawBase = CGImageSourceCreateImageAtIndex(s, 0, nil)!
    let rawMap = mapInfo(auxiliary(s))
    let base = orientedImage(rawBase, orientation: orientation)
    let gain = orientedImage(grayImage(rawMap), orientation: orientation, grayscale: true)
    writePNG(base, dir.appendingPathComponent("base.png"))
    writePNG(gain, dir.appendingPathComponent("gainmap.png"))
    var report = details(s)
    report["source_name"] = input.lastPathComponent
    report["source_orientation"] = orientation
    report["editing_orientation"] = 1
    report["editing_base_width"] = base.width
    report["editing_base_height"] = base.height
    report["editing_gain_width"] = gain.width
    report["editing_gain_height"] = gain.height
    let data = try! JSONSerialization.data(withJSONObject: report, options: [.prettyPrinted, .sortedKeys])
    try! data.write(to: dir.appendingPathComponent("manifest.json"))
    print("Extracted upright base.png, gainmap.png, manifest.json")
case "rebuild":
    guard args.count == 6 else { die("rebuild source.HEIC|JPG base.png|- gainmap.png|- matching-output.HEIC|JPG") }
    let original = source(URL(fileURLWithPath: args[2]))
    let orientation = sourceOrientation(original)
    let origBase = CGImageSourceCreateImageAtIndex(original, 0, nil)!
    let expectedBase = editingDimensions(width: origBase.width, height: origBase.height, orientation: orientation)
    let base: CGImage
    if args[3] == "-" { base = origBase }
    else {
        let bs = source(URL(fileURLWithPath: args[3]))
        guard let edited = CGImageSourceCreateImageAtIndex(bs, 0, nil) else { die("Invalid edited base") }
        guard edited.width == expectedBase.0, edited.height == expectedBase.1 else {
            die("Edited base must have dimensions \(expectedBase.0)x\(expectedBase.1)")
        }
        base = orientedImage(edited, orientation: inverseOrientation(orientation))
        guard base.width == origBase.width, base.height == origBase.height else {
            die("Edited base orientation transform produced incompatible dimensions")
        }
    }
    var aux = auxiliary(original)
    if args[4] != "-" {
        aux[kCGImageAuxiliaryDataInfoData as String] = readEditedMap(
            URL(fileURLWithPath: args[4]), original: mapInfo(aux), orientation: orientation
        )
    }
    let output = URL(fileURLWithPath: args[5])
    guard !FileManager.default.fileExists(atPath: output.path) else { die("Refusing to overwrite existing output") }
    writeGainMapImage(base, original, aux, output)
    print("Rebuilt: \(output.path)")
case "validate":
    guard args.count == 4 else { die("validate source.HEIC|JPG output.HEIC|JPG") }
    let a = details(source(URL(fileURLWithPath: args[2])))
    let b = details(source(URL(fileURLWithPath: args[3])))
    let keys = ["base_width", "base_height", "gain_width", "gain_height", "gain_format", "color_space", "orientation"]
    let differences = keys.filter { String(describing: a[$0]) != String(describing: b[$0]) }
    emitJSON(["valid": differences.isEmpty, "mismatched_fields": differences])
    if !differences.isEmpty { exit(2) }
default: die("Unknown command")
}
