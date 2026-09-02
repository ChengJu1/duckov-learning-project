# Duckov Learning Project

一个以《逃离鸭科夫》为参考、用于学习游戏开发和 AI 辅助大型工程维护的个人项目。

## 当前状态

阶段 0 已完成：仓库、Python 环境与第一个可运行窗口均已验证。项目准备进入阶段 1 的无战斗撤离原型。

## 最小可玩循环（暂定）

1. 玩家进入一张小型测试地图。
2. 玩家移动并拾取一个物品。
3. 玩家抵达撤离点。
4. 成功撤离后，物品进入局外库存。
5. 玩家可以再次出发。

这个循环用于尽早验证“进入地图 → 搜集 → 承担风险 → 撤离 → 保留收益”，暂不追求完整战斗、复杂 AI 或商业级内容。

## 近期阶段

- 阶段 0：初始化仓库、工程文档和开发环境。
- 阶段 1：实现无战斗的最小撤离循环。
- 阶段 2：加入基础战斗、生命值和一个简单敌人。
- 阶段 3：加入背包、装备、掉落和局外存储。
- 阶段 4：增加地图、敌人行为、任务与数据持久化。
- 阶段 5：性能、自动化测试、内容工具和工程复盘。

详细范围与验收标准见 [docs/project-plan.md](docs/project-plan.md)。

## 文档索引

- [项目计划](docs/project-plan.md)
- [架构说明](docs/architecture.md)
- [技术决策记录](docs/decisions/0001-initial-project-boundary.md)
- [AI 失败日志模板](docs/ai-failures/TEMPLATE.md)
- [原始协作要求](prompt.md)

## 开发环境

- 目标平台：Windows
- Python：3.14.7
- 游戏框架：pygame-ce 2.5.8
- 测试框架：pytest 9.1.1
- Git 与 GitHub 同步已验证

## 本地运行

首次进入项目时创建虚拟环境并安装依赖：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --editable ".[dev]"
```

启动当前窗口原型：

```powershell
.\.venv\Scripts\python.exe -m duckov_game
```

运行自动化测试：

```powershell
.\.venv\Scripts\python.exe -m pytest
```

## 下一步

1. 定义玩家位置、速度和地图边界的数据结构。
2. 实现键盘移动，但暂不加入物品或撤离逻辑。
3. 为移动和边界规则添加不依赖画面的自动化测试。
