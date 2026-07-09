# 实战案例 6 · 物流本体（WMS/TMS 场景）

> **场景**：电商物流系统，订单/仓库/承运商/运单/轨迹/异常
> **目标**：让 AI 1 秒回答 7 个物流/客服/运营每天问的问题

## 0. 谁在用？

| 角色 | 怎么用 | 频率 |
|------|--------|------|
| 物流经理 | 看延误/异常率 | 每天 |
| 客服 | 用 Claude 问（'运单状态'） | 每天 |
| 数据分析师 | 写新查询 | 每周 |
| 开发者（你） | 跑 logistics-query.py | 1 次 |

**这套系统不是给业务方写代码用的**——是给开发者搭好，让业务方用友好界面（仪表盘 / Claude Desktop / 自然语言）。

## 1. 业务问题

物流经理/客服每天问：
- "运单 SF1234567890 现在到哪了？"
- "现在哪些运单在运输中？"
- "各承运商运了多少？"
- "哪些运单延误了？"
- "异常类型分布？"
- "异常率多高？"
- "各仓库出了多少货？"

## 2. 跑 demo

```bash
cd ~/Documents/projects/ai/ontology/05-real-cases/logistics
python3 logistics-query.py
```

**真实输出**（已验证）：

```
数据校验：✅ 通过

Q1: 运单 SF1234567890 的轨迹
  2026-07-01T18:00:00  [Pickup]  上海主仓
  2026-07-02T08:00:00  [Arrival]  上海浦东
  2026-07-03T10:30:00  [Delivered]  上海浦东客户

Q2: 运输中的运单
  SF3456789012  王五  顺丰速运
  SF5678901234  孙七  顺丰速运
  YT8901234567  王五  圆通速递

Q3: 各承运商运单数
  顺丰速运  4 单
  圆通速递  3 单
  中通快递  1 单

Q4: 延误的运单（实际 > 预计）
  ZTO4567890123  赵六  预计 2026-07-07T18:00:00  实际 2026-07-09T09:00:00

Q5: 异常类型分布
  延误  1 次
  破损  1 次
  丢件  1 次

Q6: 异常运单
  1 异常 / 8 总运单 = 12.5%

Q7: 各仓库出货量
  深圳南头仓  3 单  /  共 21.7 kg
  北京顺义仓  2 单  /  共 5.5 kg
  上海主仓  2 单  /  共 3.5 kg
  成都双流仓  1 单  /  共 3.8 kg
```

## 3. 业务价值

| 不用本体 | 用本体 |
|---------|--------|
| 客户问发货 → 客服翻 3 个系统 | 1 个 trackingNo → 完整轨迹 |
| 异常没预警 | 自动监控延误/破损/丢件 |
| 跨承运商数据不通 | 一张图全关联 |
| 客服响应慢 | AI 1 秒回复 |

## 4. SHACL 校验的关键规则

```turtle
# 运单号格式
ex:ShipmentShape
    a sh:NodeShape ;
    sh:targetClass ex:Shipment ;
    sh:property [
        sh:path ex:trackingNo ;
        sh:minCount 1 ;
        sh:pattern "^[A-Z]{2,3}\\d{10,12}$" ;   # SF/ZTO/YT+10-12 位
    ] .

# 订单重量不能超 1 吨
ex:OrderShape
    a sh:NodeShape ;
    sh:targetClass ex:Order ;
    sh:property [
        sh:path ex:orderWeight ;
        sh:minInclusive 0 ;
        sh:maxInclusive 1000 ;
    ] .
```

## 5. 进阶练习

1. "本月最常延误的承运商"
2. "未送达的运单 + 客户"
3. "每个仓库的准时率"
4. "过去 7 天的异常趋势"
5. "丢件率最高的路线"
6. "运单轨迹完整度（应该 4-5 个事件）"

## 6. 实际场景拓展

加这些实体：
- `ex:Hub`（中转中心）
- `ex:Driver`（司机）
- `ex:Vehicle`（车辆）
- `ex:CustomerSignature`（签收凭证）
- `ex:Insurance`（保价/保险）

## 7. 跟 AI Agent 集成

```python
# 客户问："我的快递到哪了"
def track(tracking_no: str) -> str:
    q = f"""
    PREFIX ex: <http://logistics.com/>
    SELECT ?time ?type ?location WHERE {{
        ?s a ?vt ; ex:trackingNo "{tracking_no}" .
        FILTER (?vt = ex:GroundShipment || ?vt = ex:AirShipment || ?vt = ex:SeaShipment)
        ?ev ex:eventOf ?s ; ex:eventTime ?time ;
            ex:eventType ?type ; ex:eventLocation ?location .
    }} ORDER BY ?time
    """
    return format_result(g.query(q))
```

## 8. 文件清单

```
logistics/
├── README.md
├── logistics-query.py              ← 7 个查询全跑通
└── data/
    ├── logistics-ont.ttl          ← 本体（4 仓库/3 承运商/5 客户/8 订单/8 运单/10 事件/3 异常）
    ├── logistics-shapes.ttl       ← SHACL 规则
    └── logistics-data.ttl          ← 业务数据
```
