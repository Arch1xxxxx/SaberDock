import SwiftUI
import AppKit
import UniformTypeIdentifiers

func L(_ english: String, _ chinese: String) -> String {
    (ProcessInfo.processInfo.environment["SABERDOCK_LANGUAGE"] ?? UserDefaults.standard.string(forKey: "interfaceLanguage")) == "zh-Hans" ? chinese : english
}

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
struct VersionOption: Decodable, Identifiable { var id: String; var label: String }
struct AVPEnvironment: Decodable { var gameVersions: [VersionOption]; var toolchainVersions: [VersionOption]; var selectedGame: String; var selectedToolchain: String; var ready: Bool; var version: String; var avpRoot: String; var avpApp: String; var store: String; var team: String; var bundle: String; var runtimeApp: String; var gameTree: String; var apk: String; var sourceObb: String; var issues: [String] }
struct Headset: Decodable, Identifiable { var id: String; var name: String; var state: String; var model: String }

final class LibraryModel: ObservableObject {
    @Published var language = ProcessInfo.processInfo.environment["SABERDOCK_LANGUAGE"] ?? UserDefaults.standard.string(forKey: "interfaceLanguage") ?? "en" {
        didSet {
            UserDefaults.standard.set(language, forKey: "interfaceLanguage")
            if !unavailable {
                status = L("Ready", "就绪")
                logs = []
                notice = nil
                error = nil
                invoke(["scan", "--root", root]) { [weak self] value in
                    self?.acceptLibrary(value)
                    self?.inspectEnvironment()
                }
            }
        }
    }
    @Published var environment: AVPEnvironment?
    @Published var setupOpen = false
    @Published var team = ""
    @Published var avpRoot = ""
    @Published var avpApp = ""
    @Published var store = ""
    @Published var gameVersion = ""
    @Published var toolchainVersion = ""
    @Published var library: Library?
    @Published var selected: String?
    @Published var root = ProcessInfo.processInfo.environment["SABER_LIBRARY_ROOT"] ?? UserDefaults.standard.string(forKey: "libraryRoot") ?? FileManager.default.homeDirectoryForCurrentUser.appendingPathComponent("Music/SaberDock Library").path
    @Published var appName = (UserDefaults.standard.string(forKey: "headsetAppName").map { $0 == "SaberDock 自定义歌曲" ? "SaberDock Custom Songs" : $0 }) ?? "SaberDock Custom Songs"
    @Published var deviceID = UserDefaults.standard.string(forKey: "headsetID") ?? ""
    @Published var headsets: [Headset] = []
    @Published var busy = false
    @Published var scanning = false
    @Published var editingName = false
    @Published var discovering = false
    @Published var status = L("Preparing library…", "正在准备曲库…")
    @Published var logs: [String] = []
    @Published var error: String?
    @Published var notice: String?
    @Published var lastUpdate = UserDefaults.standard.string(forKey: "lastUpdate") ?? ""
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
        if root != lib.root { root = lib.root; persist() }
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
        environment = env; team = env.team; avpRoot = env.avpRoot; avpApp = env.avpApp; store = env.store; gameVersion = env.selectedGame; toolchainVersion = env.selectedToolchain
    }
    func checkEnvironment(save: Bool = false) {
        invoke([save ? "configure" : "environment", "--game-version", gameVersion, "--toolchain-version", toolchainVersion]) { [weak self] value in
            self?.acceptEnvironment(value)
            if save && self?.environment?.ready == true { self?.setupOpen = false }
        }
    }
    func firstInstall() {
        persist()
        invoke(["install", "--root", root, "--name", appName, "--device", deviceID]) { [weak self] value in
            let changed = (value as? [String: Any])?["scoresUnchanged"] as? Bool == false
            self?.notice = (changed ? L("Scores before and after installation have been backed up. ", "安装前后的成绩均已备份。") : "") + L("The custom songs app is installed. Open “\(self?.appName ?? "SaberDock")” on your headset. Use “Update Headset” for future library changes.", "独立自定义歌曲应用已安装。请在头显打开「\(self?.appName ?? "SaberDock")」。之后新增歌曲请使用「一键更新头显」。")
        }
    }
    func chooseRoot() {
        let panel = NSOpenPanel(); panel.canChooseFiles = false; panel.canChooseDirectories = true; panel.canCreateDirectories = true
        panel.message = L("Each subfolder becomes a playlist on your headset.", "每个子文件夹将成为头显中的一个曲包。"); panel.prompt = L("Use This Library", "使用此曲库")
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
        invoke(["delete", "--root", root, "--category", category, song.id]) { [weak self] value in self?.acceptLibrary(value); self?.status = L("Removed “\(song.title)”. It will be removed from the headset at the next sync.", "已删除「\(song.title)」，下次同步将从头显移除") }
    }
    func restoreSong() {
        guard !unavailable else { return }
        invoke(["restore", "--root", root, "--category", current?.name ?? ""]) { [weak self] value in self?.acceptLibrary(value) }
    }
    func openSongSource(_ song: Song) {
        let source = URL(fileURLWithPath: song.sourcePath)
        var isDirectory: ObjCBool = false
        guard FileManager.default.fileExists(atPath: source.path, isDirectory: &isDirectory) else {
            error = L("The source for “\(song.title)” was moved or deleted. Refresh your library and try again.\n\(source.path)", "「\(song.title)」的源谱面已移动或删除，请刷新曲库后重试。\n\(source.path)")
            return
        }
        let folder = isDirectory.boolValue ? source : source.deletingLastPathComponent()
        guard NSWorkspace.shared.open(folder) else {
            error = L("Could not open the source folder for “\(song.title)” in Finder.\n\(folder.path)", "无法在访达中打开「\(song.title)」的源文件夹。\n\(folder.path)")
            return
        }
        if !isDirectory.boolValue { NSWorkspace.shared.activateFileViewerSelecting([source]) }
    }
    func openLibrary() { NSWorkspace.shared.open(URL(fileURLWithPath: current?.path ?? root)) }
    func importDialog() {
        let panel = NSOpenPanel(); panel.canChooseFiles = true; panel.canChooseDirectories = true; panel.allowsMultipleSelection = true
        panel.allowedContentTypes = [.zip, .folder]; panel.message = L("Import ZIP files, extracted maps, or a folder containing several songs.", "导入 ZIP、已解压谱面，或一个包含多首歌曲的分类文件夹。"); panel.prompt = L("Import", "导入")
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
            if result["noChanges"] as? Bool == true { self.notice = L("Your headset library is up to date. No processing or transfer is needed.", "头显曲库已经是最新，无需重复处理或传输。"); return }
            let f = DateFormatter(); f.locale = Locale(identifier: self.language); f.dateFormat = "MM-dd HH:mm"
            self.lastUpdate = f.string(from: Date()); UserDefaults.standard.set(self.lastUpdate, forKey: "lastUpdate")
            let launched = result["launchSucceeded"] as? Bool ?? false
            let same = result["scoresUnchanged"] as? Bool ?? false
            self.notice = (renameOnly ? L("App name updated. ", "应用名称已更新。") : L("Library and app name updated. ", "曲库与应用名称已更新。")) + (same ? L("Scores preserved. ", "成绩记录已保留。") : L("Scores before and after the update have been backed up. ", "更新前后的成绩均已备份。")) + (launched ? L("You can now open the app on your headset.", "可以在头显中打开使用。") : L("Fully quit the headset app, then open “\(self.appName)” manually.", "请在头显中完全退出后，手动打开「\(self.appName)」。"))
        }
    }
    func buildOnly() {
        invoke(["build", "--root", root]) { [weak self] _ in self?.notice = L("Library built and verified. Click “Update Headset” to transfer it.", "曲库已生成并通过校验。需要传到头显时，点击「一键更新头显」。") }
    }
    func invoke(_ arguments: [String], quiet: Bool = false, discoveringTask: Bool = false, done: @escaping (Any) -> Void) {
        if !quiet { busy = true; status = L("Processing…", "正在处理…"); logs = [] }
        else if !discoveringTask { scanning = true }
        let base = resource
        DispatchQueue.global(qos: .userInitiated).async {
            let process = Process(); let pipe = Pipe()
            process.executableURL = base.appendingPathComponent("runtime/bin/python3")
            process.arguments = ["-u", base.appendingPathComponent("backend.py").path] + arguments
            var env = ProcessInfo.processInfo.environment
            env["SABERDOCK_LANGUAGE"] = self.language
            env["LANG"] = self.language == "zh-Hans" ? "zh_CN.UTF-8" : "en_US.UTF-8"
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
                    if !quiet { self.error = failure; self.status = L("Operation Incomplete", "操作未完成") }
                    else if discoveringTask { self.headsets = [] }
                } else if let result {
                    done(result)
                    if !quiet { self.status = L("Ready", "就绪") }
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
                    VStack(alignment: .leading) { Text("SaberDock").font(.headline); Text(L("Folders become playlists", "文件夹就是曲包")).font(.caption).foregroundStyle(.secondary) }
                }.padding(18)
                List(selection: $model.selected) {
                    Section(L("My Playlists", "我的曲包")) {
                        ForEach(model.library?.playlists ?? []) { group in
                            HStack { Label(group.name, systemImage: "music.note.list"); Spacer(); Text("\(group.count)").font(.caption.monospacedDigit()).foregroundStyle(.secondary) }.tag(group.path)
                        }
                    }
                }.listStyle(.sidebar)
                HStack { Button { newName = ""; adding = true } label: { Label(L("New Playlist", "新建曲包"), systemImage: "plus") }; Spacer(); Button { model.chooseRoot() } label: { Image(systemName: "gearshape") }.help(L("Change library location", "更改曲库位置")) }.buttonStyle(.borderless).padding(14).disabled(model.unavailable)
                Divider()
                VStack(alignment: .leading, spacing: 8) {
                    Text(L("\(model.library?.uniqueSongs ?? 0) maps · \(model.library?.playlists.filter { $0.count > 0 }.count ?? 0) playlists", "\(model.library?.uniqueSongs ?? 0) 份谱面 · \(model.library?.playlists.filter { $0.count > 0 }.count ?? 0) 个曲包")).font(.caption)
                    Button { NSWorkspace.shared.open(URL(fileURLWithPath: model.root)) } label: { Label(L("Open Library Folder", "打开曲库文件夹"), systemImage: "folder") }.buttonStyle(.link)
                }.padding(16)
            }.navigationSplitViewColumnWidth(min: 220, ideal: 245, max: 340)
        } detail: {
            VStack(alignment: .leading, spacing: 0) {
                HStack(alignment: .top) {
                    VStack(alignment: .leading, spacing: 5) { Text(model.current?.name ?? L("My Library", "我的曲库")).font(.largeTitle.weight(.semibold)); Text(L("Drop ZIP files or extracted maps. Folder changes appear automatically.", "拖入 ZIP 或已解压的谱面；文件夹中的改动会自动显示。")).foregroundStyle(.secondary) }
                    Spacer()
                    Menu {
                        Button(L("Sort by Song Title", "按歌名排序")) { model.sortSongs("title") }
                        Button(L("Sort by Artist", "按歌手排序")) { model.sortSongs("artist") }
                        Button(L("Sort by Mapper", "按谱师排序")) { model.sortSongs("mapper") }
                        Button(L("Reverse Current Order", "倒转当前顺序")) { model.sortSongs("reverse") }
                    } label: { Label(L("Sort", "排序"), systemImage: "arrow.up.arrow.down") }.disabled(model.current?.songs.isEmpty ?? true)
                    Button { model.restoreSong() } label: { Image(systemName: "arrow.uturn.backward") }.help(L("Restore the last deleted song", "恢复上次删除的歌曲")).disabled(!(model.library?.canRestore ?? false))
                    Button { model.openLibrary() } label: { Image(systemName: "folder") }.help(L("Open this playlist in Finder", "在访达中打开此曲包"))
                    Button { model.importDialog() } label: { Label(L("Import Maps", "导入谱面"), systemImage: "plus") }
                }.padding(24).disabled(model.unavailable)
                VStack(alignment: .leading, spacing: 12) {
                    HStack {
                        Label(L("Headset App Name", "头显应用名称"), systemImage: "visionpro")
                        TextField(L("App name", "应用名称"), text: $model.appName, onEditingChanged: { model.editingName = $0 }).textFieldStyle(.roundedBorder).frame(maxWidth: 310).onChange(of: model.appName) { model.persist() }
                        Button(L("Rename Only", "仅改名称")) { model.update(renameOnly: true) }.disabled(model.appName.trimmingCharacters(in: .whitespaces).isEmpty)
                    }
                    HStack {
                        Picker(L("Update To", "更新到"), selection: $model.deviceID) {
                            Text(L("Select Vision Pro Automatically", "自动选择 Vision Pro")).tag("")
                            ForEach(model.headsets) { device in Text(device.name + " · Vision Pro").tag(device.id) }
                        }.frame(maxWidth: 410).onChange(of: model.deviceID) { model.persist() }
                        Button { model.discover() } label: { Image(systemName: "arrow.clockwise") }.help(L("Refresh headsets", "刷新头显"))
                        Spacer()
                        Text(model.headsets.isEmpty ? L("Unlock your headset and connect to the same Wi-Fi", "请解锁头显并连接同一 Wi-Fi") : L("\(model.headsets.count) headset(s) found", "已发现 \(model.headsets.count) 台头显")).font(.caption).foregroundStyle(.secondary)
                    }
                }.padding(18).background(.quaternary.opacity(0.4), in: RoundedRectangle(cornerRadius: 12)).padding(.horizontal, 24).disabled(model.unavailable)
                HStack {
                    Label(model.environment?.ready == true ? L("Local game files selected", "本地游戏文件已选择") : L("Check your AVP Play installation settings", "请先检查 AVP Play 安装设置"), systemImage: model.environment?.ready == true ? "checkmark.circle" : "exclamationmark.circle").font(.caption).foregroundStyle(model.environment?.ready == true ? Color.secondary : Color.orange)
                    Spacer(); Button(L("Installation Settings…", "安装设置…")) { model.setupOpen = true }.buttonStyle(.link).disabled(model.unavailable)
                }.padding(.horizontal, 24).padding(.top, 12)
                if let errors = model.library?.errors, !errors.isEmpty {
                    DisclosureGroup { ForEach(errors, id: \.self) { Text($0).font(.caption).textSelection(.enabled) } } label: { Label(L("\(errors.count) issue(s) to resolve before updating", "\(errors.count) 项需要处理，更新前请移除或修正"), systemImage: "exclamationmark.triangle.fill").foregroundStyle(.orange) }.padding(.horizontal, 24).padding(.top, 16)
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
                                Button { model.moveSong(song, by: -1) } label: { Image(systemName: "chevron.up") }.buttonStyle(.borderless).help(L("Move up", "上移")).disabled(model.unavailable || group.songs.first?.id == song.id)
                                Button { model.moveSong(song, by: 1) } label: { Image(systemName: "chevron.down") }.buttonStyle(.borderless).help(L("Move down", "下移")).disabled(model.unavailable || group.songs.last?.id == song.id)
                                Button(role: .destructive) { deleteCategory = group.name; pendingDelete = song } label: { Image(systemName: "trash") }.buttonStyle(.borderless).help(L("Remove from this playlist", "从此曲包删除")).disabled(model.unavailable)
                                Button { model.openSongSource(song) } label: { Image(systemName: "folder") }.buttonStyle(.borderless).help(L("Open the source in Finder; ZIP files are revealed in their containing folder", "在访达中打开源谱面；ZIP 会显示其所在文件夹并选中原文件"))
                            }.padding(.vertical, 7)
                            .contextMenu {
                                Button(L("Move up", "上移")) { model.moveSong(song, by: -1) }.disabled(model.unavailable || group.songs.first?.id == song.id)
                                Button(L("Move down", "下移")) { model.moveSong(song, by: 1) }.disabled(model.unavailable || group.songs.last?.id == song.id)
                                Divider()
                                Button(L("Delete “\(song.title)”", "删除「\(song.title)」"), role: .destructive) { deleteCategory = group.name; pendingDelete = song }.disabled(model.unavailable)
                            }
                          }.onMove { model.moveSongs(from: $0, to: $1) }
                        }.listStyle(.inset)
                    } else {
                        VStack(spacing: 12) { Image(systemName: "square.and.arrow.down.on.square").font(.system(size: 42)).foregroundStyle(.blue); Text(L("Drop maps here", "把谱面拖到这里")).font(.title2.weight(.medium)); Text(L("ZIP files and map folders join the selected playlist\nA category folder creates a playlist with the same name", "ZIP 或谱面文件夹会加入当前曲包\n整份分类文件夹会建立同名曲包")).multilineTextAlignment(.center).foregroundStyle(.secondary); Button(L("Choose Maps…", "选择谱面…")) { model.importDialog() }.disabled(model.unavailable) }.frame(maxWidth: .infinity, maxHeight: .infinity)
                    }
                    if hovering { RoundedRectangle(cornerRadius: 14).fill(.blue.opacity(0.12)).overlay { RoundedRectangle(cornerRadius: 14).strokeBorder(.blue, style: StrokeStyle(lineWidth: 2, dash: [8])) }.padding(12).allowsHitTesting(false) }
                }.onDrop(of: [UTType.fileURL], isTargeted: $hovering) { model.drop($0) }
                Divider()
                VStack(alignment: .leading, spacing: 10) {
                    HStack(spacing: 12) {
                        if model.busy || model.scanning { ProgressView().controlSize(.small) }
                        VStack(alignment: .leading, spacing: 3) { Text(model.busy ? model.status : (model.scanning ? L("Scanning library…", "正在扫描曲库…") : L("Ready · Last update: \(model.lastUpdate.isEmpty ? L("Never", "尚未更新") : model.lastUpdate)", "就绪 · 上次更新 \(model.lastUpdate.isEmpty ? L("Never", "尚未更新") : model.lastUpdate)"))).font(.subheadline); Text(L("Only new or changed songs are processed · Order and deletions apply at the next sync", "只处理新增或修改曲目 · 排序与删除将在下次同步生效")).font(.caption).foregroundStyle(.secondary) }
                        Spacer()
                        Button(L("Install", "安装")) { model.firstInstall() }.disabled(model.unavailable)
                        Button(L("Build Library Only", "仅生成曲库")) { model.buildOnly() }.disabled(model.unavailable)
                        Button { model.update() } label: { Label(model.busy ? L("Processing…", "正在处理…") : L("Update Headset", "一键更新头显"), systemImage: "arrow.up.doc.fill").padding(.vertical, 5) }.buttonStyle(.borderedProminent).disabled(model.unavailable || !(model.library?.errors.isEmpty ?? true) || model.appName.trimmingCharacters(in: .whitespaces).isEmpty)
                    }
                    DisclosureGroup(L("Activity Details", "处理详情"), isExpanded: $showLogs) {
                        ScrollView { Text(model.logs.suffix(100).joined(separator: "\n")).font(.system(.caption, design: .monospaced)).frame(maxWidth: .infinity, alignment: .leading).textSelection(.enabled) }.frame(height: 100)
                    }.font(.caption)
                }.padding(20)
            }.frame(minWidth: 700, minHeight: 620)
        }.frame(minWidth: 980, minHeight: 700)
        .environment(\.locale, Locale(identifier: model.language))
        .toolbar {
            Picker("Language", selection: $model.language) {
                Text("English").tag("en")
                Text("简体中文").tag("zh-Hans")
            }.fixedSize().disabled(model.unavailable)

            Button { model.setupOpen = true } label: { Label(L("Installation Settings", "安装设置"), systemImage: "gearshape") }.disabled(model.unavailable)
            Button { model.refresh() } label: { Label(L("Refresh Library", "刷新曲库"), systemImage: "arrow.clockwise") }.disabled(model.unavailable)
        }
        .sheet(isPresented: $model.setupOpen) {
            VStack(alignment: .leading, spacing: 16) {
                Text(L("Installation Settings", "安装设置")).font(.title2.bold())
                Text(L("Choose from the game downloads and toolchains found in AVP Play’s local folders.", "从 AVP Play 本地文件夹中识别到的游戏和工具链中选择。")).foregroundStyle(.secondary)
                Picker(L("Game Version", "游戏版本"), selection: $model.gameVersion) {
                    Text(L("Select a game version", "请选择游戏版本")).tag("")
                    ForEach(model.environment?.gameVersions ?? []) { option in Text(option.label).tag(option.id) }
                }
                Picker(L("Toolchain Version", "Toolchain 版本"), selection: $model.toolchainVersion) {
                    Text(L("Select a toolchain", "请选择 Toolchain")).tag("")
                    ForEach(model.environment?.toolchainVersions ?? []) { option in Text(option.label).tag(option.id) }
                }
                ForEach(model.environment?.issues ?? [], id: \.self) { Text($0).font(.callout).foregroundStyle(.orange).textSelection(.enabled) }
                Text(L("Missing a version? Download it and complete the game installation in AVP Play, then refresh this list. Signing settings are read automatically from AVP Play.", "未找到版本？请先在 AVP Play 下载并完成游戏安装，再刷新列表。签名设置会从 AVP Play 自动读取。")).font(.caption).foregroundStyle(.secondary)
                HStack {
                    Button(L("Refresh List", "刷新列表")) { model.checkEnvironment() }
                    Button(L("Open AVP Play", "打开 AVP Play")) { if !model.avpApp.isEmpty { NSWorkspace.shared.open(URL(fileURLWithPath: model.avpApp)) } }
                    Spacer()
                    Button(L("Close", "关闭")) { model.setupOpen = false }
                    Button(L("Save and Check", "保存并检查")) { model.checkEnvironment(save: true) }.buttonStyle(.borderedProminent)
                }
            }.padding(28).frame(width: 660).disabled(model.unavailable)
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
        .alert(L("Delete Song?", "删除歌曲？"), isPresented: Binding(get: { pendingDelete != nil }, set: { if !$0 { pendingDelete = nil } })) {
            Button(L("Cancel", "取消"), role: .cancel) { pendingDelete = nil }
            Button(L("Delete", "删除"), role: .destructive) { if let song = pendingDelete { model.deleteSong(song, category: deleteCategory) }; pendingDelete = nil }
        } message: { Text(L("Remove “\(pendingDelete?.title ?? "")” from “\(deleteCategory)” at the next sync. Use the restore button to undo. Copies in other playlists are kept.", "将「\(pendingDelete?.title ?? "")」从「\(deleteCategory)」移除，下次同步时更新到头显。可用顶部恢复按钮撤销删除；其他曲包中的同一首歌会保留。")) }
        .alert(L("New Playlist", "新建曲包"), isPresented: $adding) { TextField(L("Folder / playlist name", "文件夹 / 曲包名称"), text: $newName); Button(L("Cancel", "取消"), role: .cancel) {}; Button(L("Create", "创建")) { model.create(newName) } } message: { Text(L("The folder name becomes the playlist name on your headset.", "新建的文件夹名称会直接成为头显中的曲包名称。")) }
        .alert(L("Operation Incomplete", "操作未完成"), isPresented: Binding(get: { model.error != nil }, set: { if !$0 { model.error = nil } })) { Button(L("OK", "知道了"), role: .cancel) {} } message: { Text(model.error ?? "") }
        .alert(L("Done", "完成"), isPresented: Binding(get: { model.notice != nil }, set: { if !$0 { model.notice = nil } })) { Button(L("OK", "好"), role: .cancel) {} } message: { Text(model.notice ?? "") }
    }
}
@main struct SaberLibraryApp: App {
    var body: some Scene { WindowGroup("SaberDock") { ContentView().preferredColorScheme(.light) }.defaultSize(width: 1120, height: 780).commands { CommandGroup(replacing: .newItem) {} } }
}
