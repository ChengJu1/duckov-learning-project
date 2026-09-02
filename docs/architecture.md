# 架构说明

## 目标

让游戏规则不依赖画面框架，从而能够用自动化测试验证拾取、撤离和库存结算。画面层只负责输入、显示和声音。

## 计划中的模块边界

```text
输入事件
   ↓
应用层（开始一局、更新一帧、结束一局）
   ↓
领域层（玩家、物品、地图、撤离、库存规则）
   ↓
基础设施层（窗口、渲染、资源、存档）
```

### `src/duckov_game/domain`

纯游戏规则和数据结构。不得直接导入渲染框架，便于单元测试。

### `src/duckov_game/application`

组织用例和状态流转，例如开始一局、处理拾取、撤离结算。

### `src/duckov_game/app.py`

窗口、输入、渲染、音频、资源加载和未来的存档实现。

### `tests`

优先测试领域层规则，再补充少量应用层集成测试。

## 依赖规则

- 领域层不依赖应用层和基础设施层。
- 应用层可以依赖领域层，但不直接绑定具体渲染实现。
- 基础设施层实现应用层需要的外部能力。
- 不允许把共享可变状态散落在多个模块；一局的状态必须有明确所有者。

## 尚未确定

- 坐标、碰撞和地图数据格式。
- 局外库存的持久化方式。

这些内容应通过小型技术验证和决策记录确定，不在仓库初始化时猜测。

## 当前实现

- `src/duckov_game/app.py`：pygame 窗口生命周期和每帧事件循环。
- `src/duckov_game/__main__.py`：命令行入口；测试可限制运行帧数。
- `src/duckov_game/application/game.py`：跨局状态所有者；负责一次性结算、stash 和创建新局。
- `src/duckov_game/application/session.py`：单局状态所有者，固定执行移动、瞄准、发射、弹丸更新、拾取和撤离判定；撤离后冻结状态。
- `src/duckov_game/domain/extraction.py`：撤离区域的数据与碰撞范围。
- `src/duckov_game/domain/geometry.py`：不依赖 pygame 的矩形碰撞规则。
- `src/duckov_game/domain/item.py`：单个局内物品的位置和收集状态。
- `src/duckov_game/domain/player.py`：玩家位置、移动与瞄准方向归一化、边界规则，不依赖 pygame。
- `src/duckov_game/domain/projectile.py`：弹丸方向归一化、移动和地图边界相交规则。
- `tests/test_app.py`：无显示设备的窗口冒烟测试和参数校验。
- `tests/test_game.py`：撤离结算去重、新局重建和 stash 保留测试。
- `tests/test_player.py`：移动速度、对角移动、瞄准方向、地图边界和非法时间参数测试。
- `tests/test_projectile.py`：弹丸方向、定速移动、边界清理条件和非法参数测试。
- `tests/test_session.py`：物品拾取、撤离条件、弹丸生命周期和结束后状态冻结测试。

`Game` 的生命周期跨越多局，`GameSession` 每次按 `R` 后整体替换。这样局外库存被保留，而玩家、物品、携带数和撤离状态天然恢复初始值。

pygame 层只读取鼠标坐标与左键事件，并绘制瞄准线和弹丸；玩家中心到目标点的单位方向、弹丸生成、定速移动与地图外清理由领域层和应用层处理。目标恰好位于玩家中心时保留上一次方向，避免产生无效的零向量。
