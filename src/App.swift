import SwiftUI
import AppKit
import UniformTypeIdentifiers

struct Song: Decodable, Identifiable {
    var id: String
    var title: String
    var artist: String
    var mapper: String
    var difficulties: [String]
    var cover: String
    var sourcePath: String
    var warnings: [String]
}
struct Playlist: Decodable, Identifiable {
    var name: String
    var path: String
    var songs: [Song]
    var count: Int
    var id: String { path }
}
struct Library: Decodable { var root: String; var playlists: [Playlist]; var songCount: Int; var uniqueSongs: Int; var errors: [String]; var canRestore: Bool }
struct AVPEnvironment: Decodable { var ready: Bool; var version: String; var avpRoot: String; var avpApp: String; var store: String; var team: String; var bundle: String; var issues: [String] }
struct Headset: Decodable, Identifiable { var id: String; var name: String; var state: String; var model: String }

final class LibraryModel: ObservableObject {
    @Published var environment: AVPEnvironment?
    @Published var setupOpen = false
    @Published var team = ""
    @Published var avpRoot = ""
    @Published var avpApp = ""
    @Published var store = ""
    @Published var library: Library?
    @Published var selected: String?
    @Published var root = ProcessInfo.processInfo.environment["SABER_LIBRARY_ROOT"] ?? UserDefaults.standard.string(forKey: "libraryRoot") ?? FileManager.default.homeDirectoryForCurrentUser.appendingPathComponent("Music/Beat Saber 曲库").path
    @Published var appName = UserDefaults.standard.string(forKey: "headsetAppName") ?? "SaberDock 自定义歌曲"
    @Published var deviceID = UserDefaults.standard.string(forKey: "headsetID") ?? ""
    @Published var headsets: [Headset] = []
    @Published var busy = false
    @Published var scanning = false
    @Published var editingName = false
    @Published var discovering = false
    @Published var status = "正在准备曲库…"
    @Published var logs: [String] = []
    @Published var error: String?
    @Published var notice: String?
    @Published var lastUpdate = UserDefaults.standard.string(forKey: "lastUpdate") ?? "尚未更新"
    var timer: Timer?
    var current: Playlist? { library?.playlists.first(where: { $0.path == selected }) }
    var unavailable: Bool { busy || scanning || discovering }
    var resource: URL { Bundle.main.resourceURL! }

    func persist() {
        if ProcessInfo.processInfo.environment["SABER_LIBRARY_PREVIEW"] == "1" { return }
        UserDefaults.standard.set(root, forKey: "libraryRoot")
        UserDefaults.standard.set(appName, forKey: "headsetAppName")
        UserDefaults.standard.set(deviceID, forKey: "headsetID")
    }
    func start() {
        invoke(["init", "--root", root]) { [weak self] value in
            self?.acceptLibrary(value)
            self?.inspectEnvironment()
        }
        timer = Timer.scheduledTimer(withTimeInterval: 4, repeats: true) { [weak self] _ in
            guard let self, !self.unavailable, !self.editingName, NSApplication.shared.modalWindow == nil, !NSApplication.shared.windows.contains(where: { $0.attachedSheet != nil }) else { return }
            self.refresh(quiet: true)
        }
    }
    func acceptLibrary(_ value: Any) {
        guard let data = try? JSONSerialization.data(withJSONObject: value), let lib = try? JSONDecoder().decode(Library.self, from: data) else { return }
        library = lib
        if !lib.playlists.contains(where: { $0.path == selected }) { selected = lib.playlists.first?.path }
    }
    func refresh(quiet: Bool = false) {
        guard !unavailable else { return }
        invoke(["scan", "--root", root], quiet: quiet) { [weak self] value in self?.acceptLibrary(value) }
    }
    func discover() {
        guard !unavailable else { return }
        discovering = true
        invoke(["devices"], quiet: true, discoveringTask: true) { [weak self] value in
            guard let self, let data = try? JSONSerialization.data(withJSONObject: value), let list = try? JSONDecoder().decode([Headset].self, from: data) else { return }
            self.headsets = list
            if !list.contains(where: { $0.id == self.deviceID }) { self.deviceID = list.count == 1 ? list[0].id : "" }
            self.persist()
        }
    }
    func inspectEnvironment() {
        invoke(["environment"]) { [weak self] value in
            self?.acceptEnvironment(value)
            self?.discover()
        }
    }
    func acceptEnvironment(_ value: Any) {
        guard let data = try? JSONSerialization.data(withJSONObject: value), let env = try? JSONDecoder().decode(AVPEnvironment.self, from: data) else { return }
        environment = env; team = env.team; avpRoot = env.avpRoot; avpApp = env.avpApp; store = env.store
    }
    func saveEnvironment() {
        invoke(["configure", "--avp-root", avpRoot, "--avp-app", avpApp, "--store", store, "--team", team.trimmingCharacters(in: .whitespacesAndNewlines).uppercased()]) { [weak self] value in
            self?.acceptEnvironment(value)
            if self?.environment?.ready == true { self?.setupOpen = false }
        }
    }
    func selectEnvironmentPath(_ kind: String) {
        let panel = NSOpenPanel(); panel.canChooseFiles = kind == "app"; panel.canChooseDirectories = kind != "app"
        panel.message = kind == "app" ? "选择 AVP Play.app" : (kind == "store" ? "选择 AVP Play 下载目录（含 beatsaber140-1716）" : "选择 AVPPlay 数据目录（含 toolchains 与 jobs）")
        if panel.runModal() == .OK, let url = panel.url {
            if kind == "app" { avpApp = url.path } else if kind == "store" { store = url.path } else { avpRoot = url.path }
        }
    }
    func firstInstall() {
        persist()
        invoke(["install", "--root", root, "--name", appName, "--device", deviceID]) { [weak self] value in
            let changed = (value as? [String: Any])?["scoresUnchanged"] as? Bool == false
            self?.notice = (changed ? "安装前后的成绩均已备份。" : "") + "独立自定义歌曲应用已安装。请在头显打开「\(self?.appName ?? "SaberDock")」。之后新增歌曲请使用「一键更新头显」。"
        }
    }
    func chooseRoot() {
        let panel = NSOpenPanel(); panel.canChooseFiles = false; panel.canChooseDirectories = true; panel.canCreateDirectories = true
        panel.message = "每个子文件夹将成为头显中的一个曲包。"; panel.prompt = "使用此曲库"
        if panel.runModal() == .OK, let url = panel.url {
            root = url.path; persist(); invoke(["init", "--root", root]) { [weak self] value in self?.acceptLibrary(value) }
        }
    }
    func create(_ name: String) {
        invoke(["create", "--root", root, "--category", name]) { [weak self] value in
            self?.acceptLibrary(value)
            self?.selected = URL(fileURLWithPath: self?.root ?? "").appendingPathComponent(name).path
        }
    }
    func saveOrder(_ songs: [Song]) {
        guard !unavailable, let group = current else { return }
        invoke(["order", "--root", root, "--category", group.name] + songs.map(\.id)) { [weak self] value in self?.acceptLibrary(value) }
    }
    func moveSong(_ song: Song, by delta: Int) {
        guard var songs = current?.songs, let i = songs.firstIndex(where: { $0.id == song.id }), songs.indices.contains(i + delta) else { return }
        songs.swapAt(i, i + delta); saveOrder(songs)
    }
    func moveSongs(from: IndexSet, to: Int) {
        guard var songs = current?.songs else { return }
        songs.move(fromOffsets: from, toOffset: to); saveOrder(songs)
    }
    func sortSongs(_ key: String) {
        guard var songs = current?.songs else { return }
        if key == "reverse" { songs.reverse() }
        else { songs.sort { a,b in
            let left = key == "artist" ? a.artist : (key == "mapper" ? a.mapper : a.title)
            let right = key == "artist" ? b.artist : (key == "mapper" ? b.mapper : b.title)
            let comparison = left.localizedStandardCompare(right)
            return comparison == .orderedSame ? a.title.localizedStandardCompare(b.title) == .orderedAscending : comparison == .orderedAscending
        } }
        saveOrder(songs)
    }
    func deleteSong(_ song: Song, category: String) {
        guard !unavailable else { return }
        invoke(["delete", "--root", root, "--category", category, song.id]) { [weak self] value in self?.acceptLibrary(value); self?.status = "已删除「\(song.title)」，下次同步将从头显移除" }
    }
    func restoreSong() {
        guard !unavailable else { return }
        invoke(["restore", "--root", root, "--category", current?.name ?? ""]) { [weak self] value in self?.acceptLibrary(value) }
    }
    func openSongSource(_ song: Song) {
        let source = URL(fileURLWithPath: song.sourcePath)
        var isDirectory: ObjCBool = false
        guard FileManager.default.fileExists(atPath: source.path, isDirectory: &isDirectory) else {
            error = "「\(song.title)」的源谱面已移动或删除，请刷新曲库后重试。\n\(source.path)"
            return
        }
        let folder = isDirectory.boolValue ? source : source.deletingLastPathComponent()
        guard NSWorkspace.shared.open(folder) else {
            error = "无法在访达中打开「\(song.title)」的源文件夹。\n\(folder.path)"
            return
        }
        if !isDirectory.boolValue { NSWorkspace.shared.activateFileViewerSelecting([source]) }
    }
    func openLibrary() { NSWorkspace.shared.open(URL(fileURLWithPath: current?.path ?? root)) }
    func importDialog() {
        let panel = NSOpenPanel(); panel.canChooseFiles = true; panel.canChooseDirectories = true; panel.allowsMultipleSelection = true
        panel.allowedContentTypes = [.zip, .folder]; panel.message = "导入 ZIP、已解压谱面，或一个包含多首歌曲的分类文件夹。"; panel.prompt = "导入"
        if panel.runModal() == .OK { importURLs(panel.urls) }
    }
    func importURLs(_ urls: [URL]) {
        guard !unavailable else { return }
        var args = ["import", "--root", root, "--category", current?.name ?? ""]
        args += urls.map(\.path)
        invoke(args) { [weak self] value in self?.acceptLibrary(value) }
    }
    func drop(_ providers: [NSItemProvider]) -> Bool {
        guard !unavailable else { return false }
        let group = DispatchGroup(); let lock = NSLock(); var urls: [URL] = []
        for provider in providers where provider.hasItemConformingToTypeIdentifier(UTType.fileURL.identifier) {
            group.enter()
            provider.loadItem(forTypeIdentifier: UTType.fileURL.identifier, options: nil) { item, _ in
                var url: URL?
                if let data = item as? Data { url = URL(dataRepresentation: data, relativeTo: nil) }
                else if let value = item as? URL { url = value }
                if let url { lock.lock(); urls.append(url); lock.unlock() }
                group.leave()
            }
        }
        group.notify(queue: .main) { self.importURLs(urls) }
        return true
    }
    func update(renameOnly: Bool = false) {
        persist()
        let action = renameOnly ? "rename" : "update"
        invoke([action, "--root", root, "--name", appName, "--device", deviceID]) { [weak self] value in
            guard let self, let result = value as? [String: Any] else { return }
            if result["noChanges"] as? Bool == true { self.notice = "头显曲库已经是最新，无需重复处理或传输。"; return }
            let f = DateFormatter(); f.dateFormat = "MM-dd HH:mm"
            self.lastUpdate = f.string(from: Date()); UserDefaults.standard.set(self.lastUpdate, forKey: "lastUpdate")
            let launched = result["launchSucceeded"] as? Bool ?? false
            let same = result["scoresUnchanged"] as? Bool ?? false
            self.notice = (renameOnly ? "应用名称已更新。" : "曲库与应用名称已更新。") + (same ? "成绩记录已保留。" : "更新前后的成绩均已备份。") + (launched ? "可以在头显中打开使用。" : "请在头显中完全退出后，手动打开「\(self.appName)」。")
        }
    }
    func buildOnly() {
        invoke(["build", "--root", root]) { [weak self] _ in self?.notice = "曲库已生成并通过校验。需要传到头显时，点击「一键更新头显」。" }
    }
    func invoke(_ arguments: [String], quiet: Bool = false, discoveringTask: Bool = false, done: @escaping (Any) -> Void) {
        if !quiet { busy = true; status = "正在处理…"; logs = [] }
        else if !discoveringTask { scanning = true }
        let base = resource
        DispatchQueue.global(qos: .userInitiated).async {
            let process = Process(); let pipe = Pipe()
            process.executableURL = base.appendingPathComponent("runtime/bin/python3")
            process.arguments = ["-u", base.appendingPathComponent("backend.py").path] + arguments
            var env = ProcessInfo.processInfo.environment
            env["PYTHONHOME"] = base.appendingPathComponent("runtime").path
            env["PYTHONPATH"] = base.appendingPathComponent("python-libs").path
            env["PYTHONDONTWRITEBYTECODE"] = "1"; env["PYTHONIOENCODING"] = "utf-8"
            env["PATH"] = "/usr/bin:/bin:/usr/sbin:/sbin"
            process.environment = env; process.standardOutput = pipe; process.standardError = pipe
            var result: Any?; var failure: String?; var rawLines: [String] = []
            do {
                try process.run()
                var buffer = Data()
                func consume(_ line: Data) {
                    guard let text = String(data: line, encoding: .utf8), !text.isEmpty else { return }
                    rawLines.append(text); rawLines = Array(rawLines.suffix(30))
                    if let data = text.data(using: .utf8), let object = (try? JSONSerialization.jsonObject(with: data)) as? [String: Any], let event = object["event"] as? String {
                        if event == "result" { result = object["data"] }
                        else if event == "error" { failure = object["message"] as? String }
                        else if let message = object["message"] as? String {
                            DispatchQueue.main.async { if !quiet { self.status = message; self.logs.append(message) } }
                        }
                    } else if !quiet { DispatchQueue.main.async { self.logs.append(text) } }
                }
                while true {
                    let data = pipe.fileHandleForReading.availableData
                    if data.isEmpty { break }
                    buffer.append(data)
                    while let end = buffer.firstIndex(of: 10) { consume(buffer.subdata(in: 0..<end)); buffer.removeSubrange(0...end) }
                }
                if !buffer.isEmpty { consume(buffer) }
                process.waitUntilExit()
                if process.terminationStatus != 0, failure == nil { failure = rawLines.suffix(12).joined(separator: "\n") }
            } catch { failure = error.localizedDescription }
            DispatchQueue.main.async {
                if discoveringTask { self.discovering = false }
                else if quiet { self.scanning = false }
                else { self.busy = false }
                if let failure {
                    if !quiet { self.error = failure; self.status = "操作未完成" }
                    else if discoveringTask { self.headsets = [] }
                } else if let result {
                    done(result)
                    if !quiet { self.status = "就绪" }
                }
            }
        }
    }
}

struct Cover: View {
    let path: String
    var body: some View {
        Group {
            if let image = NSImage(contentsOfFile: path) { Image(nsImage: image).resizable().aspectRatio(contentMode: .fill) }
            else { Image(systemName: "music.note").frame(maxWidth: .infinity, maxHeight: .infinity).background(.quaternary) }
        }.frame(width: 52, height: 52).clipShape(RoundedRectangle(cornerRadius: 8))
    }
}
struct ContentView: View {
    @StateObject var model = LibraryModel()
    @State var adding = false
    @State var newName = ""
    @State var hovering = false
    @State var showLogs = false
    @State var pendingDelete: Song?
    @State var deleteCategory = ""
    var body: some View {
        NavigationSplitView {
            VStack(alignment: .leading, spacing: 0) {
                HStack(spacing: 10) {
                    Image(systemName: "music.note.house.fill").font(.system(size: 24)).foregroundStyle(.blue)
                    VStack(alignment: .leading) { Text("SaberDock 曲库").font(.headline); Text("文件夹就是曲包").font(.caption).foregroundStyle(.secondary) }
                }.padding(18)
                List(selection: $model.selected) {
                    Section("我的曲包") {
                        ForEach(model.library?.playlists ?? []) { group in
                            HStack { Label(group.name, systemImage: "music.note.list"); Spacer(); Text("\(group.count)").font(.caption.monospacedDigit()).foregroundStyle(.secondary) }.tag(group.path)
                        }
                    }
                }.listStyle(.sidebar)
                HStack { Button { newName = ""; adding = true } label: { Label("新建曲包", systemImage: "plus") }; Spacer(); Button { model.chooseRoot() } label: { Image(systemName: "gearshape") }.help("更改曲库位置") }.buttonStyle(.borderless).padding(14).disabled(model.unavailable)
                Divider()
                VStack(alignment: .leading, spacing: 8) {
                    Text("\(model.library?.uniqueSongs ?? 0) 份谱面 · \(model.library?.playlists.filter { $0.count > 0 }.count ?? 0) 个曲包").font(.caption)
                    Button { NSWorkspace.shared.open(URL(fileURLWithPath: model.root)) } label: { Label("打开曲库文件夹", systemImage: "folder") }.buttonStyle(.link)
                }.padding(16)
            }.navigationSplitViewColumnWidth(min: 220, ideal: 245, max: 340)
        } detail: {
            VStack(alignment: .leading, spacing: 0) {
                HStack(alignment: .top) {
                    VStack(alignment: .leading, spacing: 5) { Text(model.current?.name ?? "我的曲库").font(.largeTitle.weight(.semibold)); Text("拖入 ZIP 或已解压的谱面；文件夹中的改动会自动显示。").foregroundStyle(.secondary) }
                    Spacer()
                    Menu {
                        Button("按歌名排序") { model.sortSongs("title") }
                        Button("按歌手排序") { model.sortSongs("artist") }
                        Button("按谱师排序") { model.sortSongs("mapper") }
                        Button("倒转当前顺序") { model.sortSongs("reverse") }
                    } label: { Label("排序", systemImage: "arrow.up.arrow.down") }.disabled(model.current?.songs.isEmpty ?? true)
                    Button { model.restoreSong() } label: { Image(systemName: "arrow.uturn.backward") }.help("恢复上次删除的歌曲").disabled(!(model.library?.canRestore ?? false))
                    Button { model.openLibrary() } label: { Image(systemName: "folder") }.help("在访达中打开此曲包")
                    Button { model.importDialog() } label: { Label("导入谱面", systemImage: "plus") }
                }.padding(24).disabled(model.unavailable)
                VStack(alignment: .leading, spacing: 12) {
                    HStack {
                        Label("头显应用名称", systemImage: "visionpro")
                        TextField("应用名称", text: $model.appName, onEditingChanged: { model.editingName = $0 }).textFieldStyle(.roundedBorder).frame(maxWidth: 310).onChange(of: model.appName) { model.persist() }
                        Button("仅改名称") { model.update(renameOnly: true) }.disabled(model.appName.trimmingCharacters(in: .whitespaces).isEmpty)
                    }
                    HStack {
                        Picker("更新到", selection: $model.deviceID) {
                            Text("自动选择 Vision Pro").tag("")
                            ForEach(model.headsets) { device in Text(device.name + " · Vision Pro").tag(device.id) }
                        }.frame(maxWidth: 410).onChange(of: model.deviceID) { model.persist() }
                        Button { model.discover() } label: { Image(systemName: "arrow.clockwise") }.help("刷新头显")
                        Spacer()
                        Text(model.headsets.isEmpty ? "请解锁头显并连接同一 Wi-Fi" : "已发现 \(model.headsets.count) 台头显").font(.caption).foregroundStyle(.secondary)
                    }
                }.padding(18).background(.quaternary.opacity(0.4), in: RoundedRectangle(cornerRadius: 12)).padding(.horizontal, 24).disabled(model.unavailable)
                HStack {
                    Label(model.environment?.ready == true ? "AVP Play · 1.40.8 文件已就绪" : "请先检查 AVP Play 安装设置", systemImage: model.environment?.ready == true ? "checkmark.circle" : "exclamationmark.circle").font(.caption).foregroundStyle(model.environment?.ready == true ? Color.secondary : Color.orange)
                    Spacer(); Button("安装设置…") { model.setupOpen = true }.buttonStyle(.link).disabled(model.unavailable)
                }.padding(.horizontal, 24).padding(.top, 12)
                if let errors = model.library?.errors, !errors.isEmpty {
                    DisclosureGroup { ForEach(errors, id: \.self) { Text($0).font(.caption).textSelection(.enabled) } } label: { Label("\(errors.count) 项需要处理，更新前请移除或修正", systemImage: "exclamationmark.triangle.fill").foregroundStyle(.orange) }.padding(.horizontal, 24).padding(.top, 16)
                }
                ZStack {
                    if let group = model.current, !group.songs.isEmpty {
                        List {
                          ForEach(group.songs) { song in
                            HStack(spacing: 14) {
                                Text("\((group.songs.firstIndex(where: { $0.id == song.id }) ?? 0) + 1)").font(.caption.monospacedDigit()).foregroundStyle(.secondary).frame(width: 24)
                                Cover(path: song.cover)
                                VStack(alignment: .leading, spacing: 4) {
                                    Text(song.title).font(.headline)
                                    Text(song.artist + (song.mapper.isEmpty ? "" : "  ·  " + song.mapper)).font(.subheadline).foregroundStyle(.secondary)
                                    Text(song.difficulties.map { $0 == "ExpertPlus" ? "Expert+" : $0 }.joined(separator: " · ")).font(.caption).foregroundStyle(.secondary)
                                }
                                Spacer()
                                if !song.warnings.isEmpty { Image(systemName: "sparkles").foregroundStyle(.orange).help(song.warnings.joined(separator: "\n")) }
                                Button { model.moveSong(song, by: -1) } label: { Image(systemName: "chevron.up") }.buttonStyle(.borderless).help("上移").disabled(model.unavailable || group.songs.first?.id == song.id)
                                Button { model.moveSong(song, by: 1) } label: { Image(systemName: "chevron.down") }.buttonStyle(.borderless).help("下移").disabled(model.unavailable || group.songs.last?.id == song.id)
                                Button(role: .destructive) { deleteCategory = group.name; pendingDelete = song } label: { Image(systemName: "trash") }.buttonStyle(.borderless).help("从此曲包删除").disabled(model.unavailable)
                                Button { model.openSongSource(song) } label: { Image(systemName: "folder") }.buttonStyle(.borderless).help("在访达中打开源谱面；ZIP 会显示其所在文件夹并选中原文件")
                            }.padding(.vertical, 7)
                            .contextMenu {
                                Button("上移") { model.moveSong(song, by: -1) }.disabled(model.unavailable || group.songs.first?.id == song.id)
                                Button("下移") { model.moveSong(song, by: 1) }.disabled(model.unavailable || group.songs.last?.id == song.id)
                                Divider()
                                Button("删除「\(song.title)」", role: .destructive) { deleteCategory = group.name; pendingDelete = song }.disabled(model.unavailable)
                            }
                          }.onMove { model.moveSongs(from: $0, to: $1) }
                        }.listStyle(.inset)
                    } else {
                        VStack(spacing: 12) { Image(systemName: "square.and.arrow.down.on.square").font(.system(size: 42)).foregroundStyle(.blue); Text("把谱面拖到这里").font(.title2.weight(.medium)); Text("ZIP 或谱面文件夹会加入当前曲包\n整份分类文件夹会建立同名曲包").multilineTextAlignment(.center).foregroundStyle(.secondary); Button("选择谱面…") { model.importDialog() }.disabled(model.unavailable) }.frame(maxWidth: .infinity, maxHeight: .infinity)
                    }
                    if hovering { RoundedRectangle(cornerRadius: 14).fill(.blue.opacity(0.12)).overlay { RoundedRectangle(cornerRadius: 14).strokeBorder(.blue, style: StrokeStyle(lineWidth: 2, dash: [8])) }.padding(12).allowsHitTesting(false) }
                }.onDrop(of: [UTType.fileURL], isTargeted: $hovering) { model.drop($0) }
                Divider()
                VStack(alignment: .leading, spacing: 10) {
                    HStack(spacing: 12) {
                        if model.busy || model.scanning { ProgressView().controlSize(.small) }
                        VStack(alignment: .leading, spacing: 3) { Text(model.busy ? model.status : (model.scanning ? "正在扫描曲库…" : "就绪 · 上次更新 \(model.lastUpdate)")).font(.subheadline); Text("只处理新增或修改曲目 · 排序与删除将在下次同步生效").font(.caption).foregroundStyle(.secondary) }
                        Spacer()
                        Button("首次安装 / 修复") { model.firstInstall() }.disabled(model.unavailable || !(model.environment?.ready ?? false) || model.team.count != 10 || !(model.library?.errors.isEmpty ?? true))
                        Button("仅生成曲库") { model.buildOnly() }.disabled(model.unavailable)
                        Button { model.update() } label: { Label(model.busy ? "正在处理…" : "一键更新头显", systemImage: "arrow.up.doc.fill").padding(.vertical, 5) }.buttonStyle(.borderedProminent).disabled(model.unavailable || !(model.library?.errors.isEmpty ?? true) || model.appName.trimmingCharacters(in: .whitespaces).isEmpty)
                    }
                    DisclosureGroup("处理详情", isExpanded: $showLogs) {
                        ScrollView { Text(model.logs.suffix(100).joined(separator: "\n")).font(.system(.caption, design: .monospaced)).frame(maxWidth: .infinity, alignment: .leading).textSelection(.enabled) }.frame(height: 100)
                    }.font(.caption)
                }.padding(20)
            }.frame(minWidth: 700, minHeight: 620)
        }.frame(minWidth: 980, minHeight: 700)
        .toolbar {
            Button { model.setupOpen = true } label: { Label("安装设置", systemImage: "gearshape") }.disabled(model.unavailable)
            Button { model.refresh() } label: { Label("刷新曲库", systemImage: "arrow.clockwise") }.disabled(model.unavailable)
        }
        .sheet(isPresented: $model.setupOpen) {
            VStack(alignment: .leading, spacing: 16) {
                Text("连接你的 AVP Play").font(.title2.bold())
                Text("复用你已下载的 Beat Saber 1.40.8，用你自己的 Xcode 账户签名并安装独立应用。").foregroundStyle(.secondary)
                ForEach(model.environment?.issues ?? [], id: \.self) { Text($0).font(.callout).foregroundStyle(.orange).textSelection(.enabled) }
                HStack { Text("AVP Play 应用").frame(width: 110, alignment: .leading); TextField("AVP Play.app", text: $model.avpApp); Button("选择…") { model.selectEnvironmentPath("app") } }
                HStack { Text("AVP Play 数据").frame(width: 110, alignment: .leading); TextField("含 toolchains 与 jobs 的目录", text: $model.avpRoot); Button("选择…") { model.selectEnvironmentPath("data") } }
                HStack { Text("游戏下载目录").frame(width: 110, alignment: .leading); TextField("含 beatsaber140-1716 的目录", text: $model.store); Button("选择…") { model.selectEnvironmentPath("store") } }
                HStack { Text("Apple 团队 ID").frame(width: 110, alignment: .leading); TextField("自己的 10 位团队 ID", text: $model.team) }
                Text("团队 ID 可从 AVP Play 最近的安装记录自动读取；也可在 Xcode → Settings → Accounts 中确认。需要 Xcode、visionOS SDK、开发者模式和已配对的 Vision Pro。").font(.caption).foregroundStyle(.secondary)
                HStack { Button("打开 AVP Play") { if !model.avpApp.isEmpty { NSWorkspace.shared.open(URL(fileURLWithPath: model.avpApp)) } }; Spacer(); Button("关闭") { model.setupOpen = false }; Button("保存并检查") { model.saveEnvironment() }.buttonStyle(.borderedProminent) }
            }.padding(28).frame(width: 700).textFieldStyle(.roundedBorder).disabled(model.unavailable)
        }
        .onAppear {
            model.start()
            if let path = ProcessInfo.processInfo.environment["SABER_LIBRARY_SNAPSHOT"] {
                DispatchQueue.main.asyncAfter(deadline: .now() + 6) {
                    guard let window = NSApplication.shared.windows.first(where: { $0.frame.width > 800 }), let view = window.contentView else { return }
                    view.layoutSubtreeIfNeeded()
                    if let bitmap = view.bitmapImageRepForCachingDisplay(in: view.bounds) {
                        view.cacheDisplay(in: view.bounds, to: bitmap)
                        try? bitmap.representation(using: .png, properties: [:])?.write(to: URL(fileURLWithPath: path))
                    }
                }
            }
        }
        .alert("删除歌曲？", isPresented: Binding(get: { pendingDelete != nil }, set: { if !$0 { pendingDelete = nil } })) {
            Button("取消", role: .cancel) { pendingDelete = nil }
            Button("删除", role: .destructive) { if let song = pendingDelete { model.deleteSong(song, category: deleteCategory) }; pendingDelete = nil }
        } message: { Text("将「\(pendingDelete?.title ?? "")」从「\(deleteCategory)」移除，下次同步时更新到头显。可用顶部恢复按钮撤销删除；其他曲包中的同一首歌会保留。") }
        .alert("新建曲包", isPresented: $adding) { TextField("文件夹 / 曲包名称", text: $newName); Button("取消", role: .cancel) {}; Button("创建") { model.create(newName) } } message: { Text("新建的文件夹名称会直接成为头显中的曲包名称。") }
        .alert("操作未完成", isPresented: Binding(get: { model.error != nil }, set: { if !$0 { model.error = nil } })) { Button("知道了", role: .cancel) {} } message: { Text(model.error ?? "") }
        .alert("完成", isPresented: Binding(get: { model.notice != nil }, set: { if !$0 { model.notice = nil } })) { Button("好", role: .cancel) {} } message: { Text(model.notice ?? "") }
    }
}
@main struct SaberLibraryApp: App {
    var body: some Scene { WindowGroup("SaberDock 曲库") { ContentView().preferredColorScheme(.light) }.defaultSize(width: 1120, height: 780).commands { CommandGroup(replacing: .newItem) {} } }
}
