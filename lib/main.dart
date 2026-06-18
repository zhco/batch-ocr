import 'dart:io';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:google_mlkit_text_recognition/google_mlkit_text_recognition.dart';
import 'package:path_provider/path_provider.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:path/path.dart' as p;

void main() => runApp(const BatchOCRApp());

class BatchOCRApp extends StatelessWidget {
  const BatchOCRApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(title: '批量OCR', theme: ThemeData(primarySwatch: Colors.indigo), home: const HomePage(), debugShowCheckedModeBanner: false);
  }
}

class HomePage extends StatefulWidget {
  const HomePage({super.key});
  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  List<String> _imageFiles = [];
  String _dirPath = '';
  bool _running = false;
  int _progress = 0;
  String _status = '请选择图片目录';

  Future<void> _pickDir() async {
    String? dir = await FilePicker.platform.getDirectoryPath();
    if (dir == null) return;

    final exts = {'.png', '.jpg', '.jpeg', '.bmp', '.webp'};
    final all = Directory(dir).listSync().whereType<File>().where((f) => exts.contains(p.extension(f.path).toLowerCase())).map((f) => f.path).toList()..sort();

    setState(() { _dirPath = dir; _imageFiles = all; _status = '共 ${all.length} 张图片待识别'; });
  }

  Future<void> _startOCR() async {
    if (_imageFiles.isEmpty) return;
    setState(() { _running = true; _progress = 0; });

    final textRecognizer = TextRecognizer(script: TextRecognitionScript.chinese);
    final outputDir = '${(await getExternalStorageDirectory())!.path}/ocr_output';
    Directory(outputDir).createSync(recursive: true);

    int ok = 0;
    for (int i = 0; i < _imageFiles.length; i++) {
      setState(() { _status = '[${i + 1}/${_imageFiles.length}] ${p.basename(_imageFiles[i])}'; _progress = ((i + 1) / _imageFiles.length * 100).toInt(); });

      try {
        final input = InputImage.fromFilePath(_imageFiles[i]);
        final result = await textRecognizer.processImage(input);
        final lines = result.blocks.expand((b) => b.lines).map((l) => l.text).where((t) => t.isNotEmpty).join('\n');

        final outPath = '${outputDir}/${p.basenameWithoutExtension(_imageFiles[i])}.txt';
        File(outPath).writeAsStringSync(lines);
        ok++;
      } catch (_) {}
    }

    textRecognizer.close();
    setState(() { _running = false; _progress = 100; _status = '完成！成功 $ok/${_imageFiles.length}\n结果: $outputDir'; });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('批量OCR'), actions: [IconButton(icon: const Icon(Icons.folder_open), onPressed: _running ? null : _pickDir)]),
      body: Column(
        children: [
          Padding(padding: const EdgeInsets.all(12), child: Text(_status, style: const TextStyle(fontSize: 15), textAlign: TextAlign.center)),
          if (_dirPath.isNotEmpty) Padding(padding: const EdgeInsets.only(bottom: 8), child: Text(_dirPath, style: TextStyle(fontSize: 12, color: Colors.grey[600]))),
          Expanded(
            child: _imageFiles.isEmpty
                ? const Center(child: Text('点击右上角选择图片目录', style: TextStyle(color: Colors.grey)))
                : ListView.builder(itemCount: _imageFiles.length, itemBuilder: (_, i) => ListTile(dense: true, leading: const Icon(Icons.image), title: Text(p.basename(_imageFiles[i]), maxLines: 1, overflow: TextOverflow.ellipsis))),
          ),
          if (_running) Padding(padding: const EdgeInsets.symmetric(horizontal: 16), child: LinearProgressIndicator(value: _progress / 100)),
          Padding(
            padding: const EdgeInsets.all(16),
            child: SizedBox(width: double.infinity, height: 48, child: ElevatedButton(onPressed: (_running || _imageFiles.isEmpty) ? null : _startOCR, child: const Text('开始识别', style: TextStyle(fontSize: 16)))),
          ),
        ],
      ),
    );
  }
}
