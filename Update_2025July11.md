# 2025年7月11日更新说明
**更新缘由**：DeepSeekR1的思考时间过长，而且免费额度已经耗尽，所以需要短暂地更新为deepseek-v3模型以确保项目正常运行。
## 更新内容：
* 禁用DeepSeekR1系列模型的调用，更改为DeepSeek-V3模型
* 在.env文件中预先写入Qwen3系列模型的名称，供未来调用
* 增加一个AB测试文件，供项目组成员在未来快速测试模型的调用，其路径为"/aurawell/AB_test.py"
## 更新步骤：
1. 检查所有程序文件，将硬编码的"deepseek-r1-0528"或者其他DeepSeekR1系列的调用全部更改为"deepseek-v3"
2. 修改所有硬编码调用，改为从.env中读取模型名称，目前全部设置为读取"DEEPSEEK_SERIES_V3"这个环境变量，但是所有文件都可以在未来切换为同节点的Qwen系列模型
## 验证步骤
1. 在tests文件夹中创建一个基于pytest的测试文件，测试deepseek-v3模型是否可以被正确调用
2. 检查 start_aurawell.sh 和 test_macos_scripts.sh 文件，要求它们必须能正确启动新版本的项目文件
3. 检查Nignx设置，要求其可以正确启动
4. 在tests文件夹中创建一个基于pytest的测试文件，测试同节点下的QWEN_FAST对应的模型是否可以被正确调用