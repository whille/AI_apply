agent meta方法论：
	# plan mode: 我们整理这个方法论，做讨论细化， 后续落地要整理成 prd.json 用 ralph.sh 自动多 agent 执行。
	思想：好的应用是 人机结合， 人做关键决策， AI 自动设计、执行、验收。

我的思考点如下：

怎么跟踪前沿 ai 技术？ youtube， x, b 站？ 高效获取信息
怎么搜索技术知识： 
	* ai websearch 技能, 
	* github 搜索
	* B 站等 关键词视频搜索->信息提取（字幕总结优先）->识别优劣. 需要可落地的技能（搜索现有或自制）
		** 调研b 站之前的视频总结助手怎么实现的？ 比如 @有趣的程序员

怎么快速分辨技术含金量？ AI 总结 辨识？
	B 站帖子 参数（时效性、UP 粉丝数、评论数、收藏点赞数） -> AI 总结（语音）， insight

怎么理解优秀优秀项目： claude code 源码， Hermes 源码， Karpathy-llm-wiki 项目源码
	AI 总结，insight， 高价值思路 -> 设计.md
	评估： 多个测试用例，验证它的高价值性，加入设计用例

理想的 Agent 设计：
	融合各个 agent plan。含 test 设计

Agent harness skill/rules/hook：
	现有框架下， 怎么高效使用。
	/review ： subagents 代码质量，是否需要重构， 怎么自动触发交互式修改; 深度项目 review 怎么做好？
	/refactoring 好的重构怎么做？ 有没有参考模式或 skill?
	/wiki_doc 怎么适当时机 把代码 ingest 到好的文档tree， 给agent 以后整理高效的 context 
	自我进化： 借鉴 hermes 思路
	多任务拆解技术：分析 task依赖关系，用 subagents，提高并发
	还有哪些？

