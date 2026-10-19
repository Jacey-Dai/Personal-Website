# 海岸局部样板 · Art study 01

## 这轮验证什么

用户不喜欢原 SVG 的低饱和、安静旅行地图画风，希望色彩大胆、有游戏感；喜欢 Townscaper、Donut County、A Short Hike 等参考，并提供了三个 Quaternius Standard 素材包。

这轮只制作「一栋工作室＋少量植物＋海岸码头」样板，验证模型组合、材质、比例和色彩。不是完整岛屿的新布局，也不替换正式首页。不应将渲染图片当成最终地图的所有交互层。

预览入口：`art-study.html`。A/B 按钮切换同一场景的两套配色；中文说明与可访问按钮独立于图片。

## 已核实的素材

来源分支：`assets/source-packs`，固定提交 `7b16930628d5adc01c6e5f98afde99199ea21e3a`。用户实际目录名为 `assests/`，工具保留该原始拼写。

三个包内的 `License_Standard.txt` 均标注 CC0 1.0 Universal。此样板使用 Medieval 和 Nature；Downtown 已检查但未使用。实际使用包的原始声明保留在 `docs/licenses/`。

Nature 声明免费版提供 68/116 个模型，预设风格化 shader 属于 SOURCE 版本。不能声称免费包会自动获得宣传图效果。

模型与贴图：glTF JSON、外部 BIN、PNG。制作工具从 Git 提取明确选定的模型及 URI 依赖，不执行包内文件。18 个候选模型列在 `tools/extract_art_sample.py`；其中部分只用于评估，实际场景调用见渲染脚本。建筑、树皮和岩石采用平涂材质；叶片与花保留原始贴图的透明度遮罩，重新赋予明亮颜色，避免免费版本直接渲染时树冠过暗。

## 组合与调整

- Medieval：4×6 屋顶；墙／门窗模块组合成工作室；烟囱、木平台、栏杆、箱子用于海边细节。
- Nature：两种阔叶树、一棵松树、花灌木、花与两种岩石。减少密集草丛，保持路线与建筑可见。
- 原创补充：岛体、沙岸、海面、波纹、山墙填充、码头支柱、踏石、标牌及小帆船。
- 建筑改为平涂高饱和材质，弱化写实木纹和石砖；统一正交镜头与软光。
- A：珊瑚屋顶、黄墙、湖蓝海水。B：紫屋顶、淡紫墙、鲜蓝海水。两者几何、镜头和光照一致。

## 如何复现

需要 Python 3、Blender 4.3.2（glTF 导入器）、Pillow。制作依赖无需放入网站运行时。

```sh
git fetch origin refs/heads/assets/source-packs:refs/remotes/origin/assets/source-packs
python3 tools/extract_art_sample.py /tmp/island-art-sources
blender --background --threads 4 --python tools/inspect_art_models.py -- /tmp/island-art-sources
blender --background --threads 4 --python tools/render_art_sample.py -- /tmp/island-art-sources /tmp/island-art-renders
python3 tools/prepare_art_previews.py /tmp/island-art-renders /tmp/island-art-sources
npm run build
```

Cycles CPU，48 samples，1600×1200。当前 Blender 没有 OpenImageDenoise，因此不启用去噪。`.blend`、原始 PNG 和模型暂留制作目录；只将 WebP 预览图纳入 `public/art-study/`。保存的 `.blend` 有外部贴图依赖，脚本与固定源提交是复现依据，不把单独 `.blend` 当作独立交付。

## 等待反馈

屋顶／海水配色、自然物的细节是否过多、建筑是否仍过于中世纪，以及海岸与漂浮底座的关系。样板确认后再做完整五个空间、可交互分层与移动端场景。未经反馈不要把此场景直接替换全岛。
