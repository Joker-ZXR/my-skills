# Joker-ZXR Skills

个人研究skill合集，以Codex插件及GitHub marketplace方式分发。包含的skill见[SKILLS.md](SKILLS.md)。

## 安装

仓库上传到GitHub后，在目标电脑执行：

```powershell
git config --global core.longpaths true
codex plugin marketplace add https://github.com/Joker-ZXR/my-skills.git --ref main
codex plugin add my-skills@my-skills-market
codex plugin list --json
```

第一条是Windows Git长路径设置。私有仓库需要GitHub访问权限。ChatGPT账号与GitHub认证相互独立。安装后重启桌面端，在新对话中选择插件skill。

## 更新

维护电脑：修改原始skill目录，然后在本仓库运行：

```powershell
python .\sync-skills.py 1.0.2 --add-only
git add .
git commit -m "Add local skills in 1.0.2"
git push origin main
```

下次使用新的递增版本号。同步脚本读取当前用户的`~/.codex/skills`和`~/.agents/skills`。`--add-only` 仅加入仓库尚无的技能，保留全部已有技能和附带资源；同名技能跳过。本机没有新增技能时不改版本或文件。Linux/macOS 可使用 `python3 sync-skills.py 1.0.2 --add-only`。

省略 `--add-only` 会按本机来源完整替换插件目录，包括删除本机没有的技能和资源；仅在明确需要完整重建且来源齐全时使用。

使用电脑：

```powershell
codex plugin marketplace upgrade my-skills-market
codex plugin add my-skills@my-skills-market
codex plugin list --json
```

第一条刷新Git仓库快照，第二条请求安装或刷新当前插件。核对输出中的版本号；若客户端仍保留旧版，在插件界面更新或卸载后重装这个插件。重启桌面端并开新对话。该流程需要主动执行，不会仅因登录账号或修改本地文件就自动更新。

## 打包范围与运行依赖

收录两个用户目录中的独立skill，保留第三方LICENSE、NOTICE和来源说明。现有插件缓存、OpenAI系统skill、Python虚拟环境、node_modules、本机运行文件和BGGG历史项目输出不纳入仓库。没有为第三方内容统一指定新许可证。

1.0.2 新增 10 个独立技能，主技能总数为 47；原有 37 个技能和期刊资源保持原样。新增内容及跨机器路径适配见 [新增技能说明](plugins/my-skills/LOCAL-ADDITIONS.md)。

`awesome-journal-skills`依赖的完整期刊库位于插件的`resources/Awesome-Journal-Skills`。其入口在导出时改为相对路径，内部模块布局保持原样。

`publication-chart-skill`导出副本中的固定Windows解释器路径改为当前环境检查；原电脑字体状况不再当作目标电脑的既定事实。其固定依赖版本记录被保留。

所有源skill仍保留在原目录。插件安装不等于复制Python环境、安装Tabbit或editppt等外部工具，也不等于已经运行验证每个科研流程。源目录中的同名skill和插件skill可能同时出现，调用时选择`my-skills`插件提供的版本。

## 网页端

GitHub仓库上传与本地CLI安装不会自动创建网页端插件。在有相应权限的ChatGPT工作区，通过Admin → Plugins → Add → Import marketplace导入：

- Source：`https://github.com/Joker-ZXR/my-skills`
- Path：留空
- Branch：`main`

管理员设置使用范围，成员安装后使用。默认每日同步，也可通过Sync now立即请求同步。本包没有配置MCP；具体skill是否能在网页完成任务仍取决于工具与运行环境。个人账号没有上述工作区入口时，不应假定GitHub仓库能直接安装到网页端。

## 官方说明

- [插件打包](https://developers.openai.com/plugins/build/plugins)
- [CLI命令](https://learn.chatgpt.com/docs/cli/reference)
- [工作区GitHub导入与同步](https://learn.chatgpt.com/docs/enterprise/plugin-management)
