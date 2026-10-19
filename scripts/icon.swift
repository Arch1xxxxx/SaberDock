import AppKit
let output = URL(fileURLWithPath: CommandLine.arguments[1])
let folder = output.deletingLastPathComponent().appendingPathComponent("SaberDock.iconset")
try FileManager.default.createDirectory(at: folder, withIntermediateDirectories: true)
func render(_ size: Int) throws -> Data {
    let image = NSImage(size: NSSize(width: size, height: size)); image.lockFocus()
    let scale = CGFloat(size) / 1024
    NSGraphicsContext.current!.cgContext.scaleBy(x: scale, y: scale)
    NSColor(calibratedRed: 0.09, green: 0.15, blue: 0.3, alpha: 1).setFill()
    NSBezierPath(roundedRect: NSRect(x: 45, y: 45, width: 934, height: 934), xRadius: 210, yRadius: 210).fill()
    for (x,dx,color) in [(CGFloat(270),CGFloat(260),NSColor.systemCyan),(CGFloat(754),CGFloat(-260),NSColor.systemPink)] {
        color.setStroke(); let path = NSBezierPath(); path.lineCapStyle = .round; path.lineWidth = 56
        path.move(to: NSPoint(x: x, y: 330)); path.line(to: NSPoint(x: x + dx, y: 750)); path.stroke()
    }
    NSColor.white.setStroke(); let dock = NSBezierPath(); dock.lineWidth = 45; dock.lineCapStyle = .round
    dock.move(to: NSPoint(x: 250, y: 230)); dock.line(to: NSPoint(x: 774, y: 230)); dock.stroke()
    image.unlockFocus()
    return NSBitmapImageRep(data: image.tiffRepresentation!)!.representation(using: .png, properties: [:])!
}
for n in [16,32,128,256,512] {
    try render(n).write(to: folder.appendingPathComponent("icon_\(n)x\(n).png"))
    try render(n*2).write(to: folder.appendingPathComponent("icon_\(n)x\(n)@2x.png"))
}
let p = Process(); p.executableURL = URL(fileURLWithPath: "/usr/bin/iconutil"); p.arguments = ["-c","icns",folder.path,"-o",output.path]; try p.run(); p.waitUntilExit()
if p.terminationStatus != 0 { exit(p.terminationStatus) }
try FileManager.default.removeItem(at: folder)
