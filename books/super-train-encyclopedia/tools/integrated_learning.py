"""Child-facing principle reveals inserted after specific train cards.

The chapter builder keeps train cards and these learning blocks separate so a
future card reorganization cannot silently discard the integrated explanations.
Each key is the number of the train card that should be followed immediately by
the Markdown value.
"""

from __future__ import annotations

import re


LEARNING_BLOCKS_AFTER_CARD: dict[int, str] = {
    4: """### 🔍 打开火箭号看看：火怎样推动车轮？

![蒸汽机车侧面剖开后，火烧锅炉、蒸汽推动活塞、连杆带动车轮的图](images/principles/steam-power.svg)

火把锅炉里的水烧热。水变成蒸汽，跑进汽缸。蒸汽推着活塞来回走，红色连杆就带着大轮转起来。

<details>
<summary>🔎 给大人再讲一点</summary>

锅炉把燃料的化学能变成蒸汽的内能。配汽机构让蒸汽轮流进入汽缸两侧，活塞往复运动，连杆再把它变成车轮转动。图中省略了很多阀门和管路。

</details>

**一起找：** 在火箭号或其他蒸汽机车的照片里，找一根连着大轮的杆。真实机车很烫，只能远看。""",

    5: """### 🔍 再看脚下：钢轮为什么爱走钢轨？

![侧面看钢轮沿钢轨向前滚动，重量向轨道下方传递的图](images/principles/steel-wheel-rail.svg)

钢轮很硬，钢轨也很硬。轮子滚过时，它们只会压扁一点点，所以火车能省力地向前走。轨道还把重重的车身托住。

<details>
<summary>🔎 给大人再讲一点</summary>

钢轮和钢轨接触时变形较小，滚动阻力通常很低。重量会沿“车轮—钢轨—扣件—轨枕或轨道板—道床和路基”逐层分散。

</details>

**一起找：** 只从照片、车厢或博物馆护栏外看车轮；不靠近运行中的轨道。""",

    8: """### 🔍 看真正的车轮：里面那圈凸边是什么？

![博物馆里落在钢轨上的真实轮对，车轮内侧能看见轮缘](images/principles/photos/p001-wheel-on-rail.webp)

*实拍：钢轨上的轮对。车轮内侧那圈凸边就是轮缘。· [图片署名](PRINCIPLE_PHOTO_CREDITS.md#principle-photo-p001-wheel-on-rail)*

先看真车轮：两圈凸边都藏在两条钢轨的里侧。

![轮对在轨道中间和偏向一侧时，轮缘位置的对比图](images/principles/wheel-flange.svg)

轮缘藏在车轮内侧。火车走在中间时，它常常不用碰钢轨。车轮偏得太多，轮缘才来挡一下。

<details>
<summary>🔎 给大人再讲一点</summary>

轮对的踏面并非简单圆柱。轮对横向移动时，两侧会出现不同的滚动半径，帮助它居中和通过曲线；轮缘主要是最后的限位帮手。

</details>

**一起找：** 隔着博物馆护栏，指一指轮缘藏在钢轮的哪一侧。""",

    20: """### 🔍 打开一辆柴电机车：发动机为什么先发电？

![柴油机、发电机、电动机和车轮按顺序连接的简图](images/principles/diesel-paths.svg)

柴油机先让发电机转，发电机再把电送给车轮旁的电动机。

现在去大图里，把这三样机器再找一遍。

![柴电机车写实剖面，车内柴油机连接发电机，电缆再通向车轴旁的电动机](images/principles/generated/diesel-electric-cutaway.webp)

*写实剖面插图（AI 生成，不是实拍）：只用来帮助找到大部件。· [生成说明](GENERATED_PRINCIPLE_IMAGES.md#diesel-electric-cutaway)*

<details>
<summary>🔎 给大人再讲一点</summary>

这是一辆通用柴电机车的教学剖面，不对应某个具体型号。柴油机械车和柴油液力车会用不同办法传力，不能只凭发动机声音判断传动形式。

</details>

**一起找：** 顺着图从柴油机指到发电机，再沿电缆指到车轮。""",

    127: """### 🔍 YC1 刹车时，电会跑回电池吗？

![从左到右三格显示车轮转动、电动机变成发电机、能量存进电池](images/principles/regenerative-braking.svg)

刹车时，车轮还在转。车轮带着电动机转，电动机变成发电机。做出的一部分电，就跑回电池里了。

<details>
<summary>🔎 给大人再讲一点</summary>

再生制动能否工作，还取决于电网或储能装置能否接收能量。低速、黏着不足或系统不能接收时，列车会混合使用空气制动和摩擦制动等办法。

</details>

**一起找：** 坐稳扶好，听一听进站减速和出站加速的声音有什么不同。""",

    32: """### 🔍 跟着 Eurostar 换线路：头顶的电都一样吗？

![同一辆列车从一种架空线供电区开到另一种供电区，电先经过车内设备再到车轮电动机](images/principles/overhead-ac-dc.svg)

不同线路送来的电可能不一样。受电弓先把电接进车里。车里的机器像“电的翻译员”，把它变成电动机能用的样子。列车就能继续跑。

<details>
<summary>🔎 给大人再讲一点</summary>

线路可能采用不同电压和交流、直流制式。多制式列车会用变压器、变流器等设备处理电力，但能否跨线还取决于受电方式、信号、轮轨条件和线路许可。

</details>

**一起找：** 只从车窗或照片比较不同线路的电线；永远不碰铁路供电设备。""",

    52: """### 🔍 把 500 系和 700 系放一起：鼻子为什么不同？

| 细长的 500 系 | 扁宽的 700 系 |
| --- | --- |
| ![细长尖鼻的 500 系新干线实车](images/trains/t048-shinkansen-500.webp) | ![扁宽车头的 700 系新干线实车](images/trains/t052-shinkansen-700.webp) |
| [图片署名](IMAGE_CREDITS.md#img-t048-shinkansen-500) | [图片署名](IMAGE_CREDITS.md#img-t052-shinkansen-700) |

先看真车：500 系的鼻子细长，700 系的鼻子更宽、更扁。

![两种流线形车头让空气沿车身分开的图](images/principles/aerodynamic-nose.svg)

列车跑得快，车头会先撞到空气。500 系的细鼻子、700 系的宽鼻子，都让空气顺着车身绕过去。它们长得不一样，却都在轻轻推开风。

<details>
<summary>🔎 给大人再讲一点</summary>

列车进入隧道时会压缩前方空气，车头形状也要帮忙控制压力波。气动设计还包括车身接缝、转向架区域、车底和车尾。合适的形状取决于速度、隧道、噪声、车内空间和运营条件；鼻子不是越长就一定越快。

</details>

**一起找：** 用手指沿两辆车的车头和车顶各描一次，说说哪里最不一样。""",

    56: """### 🔍 抬头看 E5：车顶的“胳膊”碰着什么？

![E5 系新干线车顶的真实受电弓，顶部滑板接触架空线](images/principles/photos/p002-e5-pantograph.webp)

*实拍：E5 系车顶的受电弓。· [图片署名](PRINCIPLE_PHOTO_CREDITS.md#principle-photo-p002-e5-pantograph)*

先看真车：黑色滑板在最上面，正好顶住头顶的电线。

![受电弓顶着架空接触线，电流进入列车的简图](images/principles/pantograph.svg)

受电弓像一只会伸缩的胳膊。它的顶端轻轻顶住电线。列车向前跑，滑板就沿着电线滑，把电接进车里。

<details>
<summary>🔎 给大人再讲一点</summary>

弹簧或气动装置给受电弓受控的向上力。高速时受电弓和接触线都会振动，所以接触线张力、受电弓外形和主动控制要一起设计。

</details>

**一起找：** 只在封闭车厢、站台安全区或照片里找受电弓。车顶和电线永远不能碰。""",

    159: """### 🔍 跟着燕房线：前面有车时，它会怎么做？

![两格图显示前方有列车时红灯等待，前方空出后收到绿色前进许可](images/principles/signals.svg)

前面的铁轨上还有车，燕房线就停下等。前车开远了，系统才告诉它：“可以继续走啦。”图里的红和绿，讲的是“先等一等”和“可以走了”。

<details>
<summary>🔎 给大人再讲一点</summary>

轨道电路、计轴器、联锁和列车控制系统会共同工作。图中的红绿只是帮助理解“等候／获准前进”，真实信号含义因线路和规则而异，不能只凭一个灯色下结论。

</details>

**一起找：** 只从车内找一个信号或驾驶室显示，不猜列车下一步一定怎样开。""",

    69: """### 🔍 地铁旁边那只“鞋”在碰什么？

![真实车辆下方的集电靴接触带保护结构的第三轨](images/principles/photos/p004-third-rail-shoe.webp)

*实拍：下接触式第三轨集电靴。别的地铁可能长得不同。· [图片署名](PRINCIPLE_PHOTO_CREDITS.md#principle-photo-p004-third-rail-shoe)*

先看真车：车底伸出的黑色集电靴，正贴着旁边有护罩的供电轨。

![车上的集电靴贴着轨旁供电轨滑行的简图](images/principles/third-rail.svg)

有些地铁不从头顶取电。车底伸出一只集电靴，贴着旁边的供电轨滑。电就从这里进入列车。供电轨有保护罩，也仍然非常危险。

<details>
<summary>🔎 给大人再讲一点</summary>

集电靴可能从供电轨上面、侧面或下面接触，电流通常再经走行轨等回到供电系统。不同地铁的供电办法并不相同。

</details>

**一起找：** 只在车内看看线路有没有架空线；绝不靠近、触碰或跨越轨旁设备。""",

    75: """### 🔍 真正的道岔：哪一小段钢轨会动？

![真实铁路道岔近照，两根尖尖的活动钢轨通向分岔](images/principles/photos/p005-switch-points.webp)

*实拍：道岔里细长的尖轨。· [图片署名](PRINCIPLE_PHOTO_CREDITS.md#principle-photo-p005-switch-points)*

先看真道岔：两根尖尖的钢轨很细，它们可以左右摆动。

![尖轨摆向不同位置后，把车轮带向两条路线之一的俯视图](images/principles/points.svg)

火车没有方向盘。来到岔路前，细长的尖轨会先摆好。车轮贴着选好的钢轨，就走向那一边。

<details>
<summary>🔎 给大人再讲一点</summary>

道岔还包括辙叉和护轨。联锁系统会检查位置、锁闭状态和线路占用，防止互相冲突的路线同时开放。

</details>

**一起找：** 从车窗或公开视频远看分岔，走过以后再说自己去了哪一边。""",

    124: """### 🔍 跟着 733 系过雪地：轮子为什么会滑？

![两格图比较钢轮在干燥钢轨上稳稳滚动，以及在湿滑钢轨上空转](images/principles/adhesion-traction.svg)

干净的钢轨能让车轮稳稳滚。雨水、落叶和冰雪会让它变滑。列车会把力量放小一点，有些机车还会撒一点砂。

<details>
<summary>🔎 给大人再讲一点</summary>

牵引力和制动力都经很小的轮轨接触区传递。防空转、防滑控制会迅速调整每根车轴的力，撒砂则能改善局部接触条件。

</details>

**一起找：** 雨天只在车厢里听起步声，和晴天比较是否一样平顺。""",

    129: """### 🔍 车厢下面的小架子，为什么会转？

![真实铁路转向架，可见两组轮对、弹簧和减振器](images/principles/photos/p003-bogie-suspension.webp)

*实拍：车厢下面的一副转向架。· [图片署名](PRINCIPLE_PHOTO_CREDITS.md#principle-photo-p003-bogie-suspension)*

先看真车：两组轮对和好几只弹簧，都装在同一个小架子上。

![长车厢下面的前后转向架顺着弯道转动的图](images/principles/axle-bogie.svg)

两组轮对和弹簧装在一个会转的小架子里，它叫转向架。长车厢过弯时，前后转向架会各自顺着钢轨转一点。

<details>
<summary>🔎 给大人再讲一点</summary>

转向架组织轮对、轴箱、悬挂、减振和制动装置。也有单轴、共享转向架和其他结构，不能只靠外观看见的轮子数量判断。

</details>

**一起找：** 在侧面照片或博物馆护栏外，数一节车厢下面有几副转向架。""",

    80: """### 🔍 看 381 系过弯：外侧钢轨为什么高一点？

刚才那张照片里，381 系的车身正向弯道里面斜过去。

![弯道外侧钢轨抬高，让列车向弯心倾斜的剖面图](images/principles/curve-cant.svg)

火车转弯时，身体会想往外晃。把外侧钢轨垫高，车身就会向弯里斜一点。381 系还能让车体再多倾一点。

<details>
<summary>🔎 给大人再讲一点</summary>

外轨超高让轨道支撑力得到朝向曲线中心的分量。合适的超高和速度、曲线半径有关；摆式车体可以额外内倾，但不会改变钢轨本身的高度差。

</details>

**一起找：** 从车头公开视频或远处照片看弯道，不为看钢轨探身。""",

    83: """### 🔍 车轮咚一下，床为什么只轻轻晃？

![真实转向架上的弹簧和减振器](images/principles/photos/p003-bogie-suspension.webp)

*实拍：轮子上方真的有弹簧和减振器。· [图片署名](PRINCIPLE_PHOTO_CREDITS.md#principle-photo-p003-bogie-suspension)*

先看真车：轮子上方的大弹簧可以压短，旁边的减振器会拉住摇晃。

![两格图显示车轮撞到小凸起，而车厢里的小熊只轻轻晃动](images/principles/suspension-comfort.svg)

车轮撞到不平的地方，弹簧就压短。减振器把大颠簸变成小摇晃，床上的小熊就不会被抛起来。

<details>
<summary>🔎 给大人再讲一点</summary>

常见转向架有一级和二级悬挂。弹簧储存并释放能量，减振器逐渐耗散振动；设计要同时照顾轮轨接触和车辆稳定，并非越软越好。

</details>

**一起找：** 坐稳扶好，比较车轮声和座椅晃动：每次“咚”都一样大吗？""",

    100: """### 🔍 机车一动，后面的车怎样跟上？

![从左到右显示前车先动、车钩拉紧、后车跟上的三步图](images/principles/coupler-force.svg)

车钩把一辆车连到下一辆。前车先动，车钩慢慢拉紧。拉力再传到后车，长长的车队就一节一节跟上。

<details>
<summary>🔎 给大人再讲一点</summary>

牵引和制动会在列车中形成纵向拉力或压力。缓冲和弹性元件会吸收部分冲击，司机也要平稳操纵，避免过大的纵向力。

</details>

**一起找：** 只在照片或开放展区护栏外找车钩，绝不进入两车之间。""",

    101: """### 🔍 车头要停车，最后一节怎么知道？

![三节货车由一根蓝色空气管贯穿，每节车用自己的空气罐推动刹车块](images/principles/air-brake.svg)

图里的蓝色长管，从车头一直连到最后一节。车头要刹车，每节车都会“听见”。每节车再用自己的小气罐，把刹车推上去。

<details>
<summary>🔎 给大人再讲一点</summary>

图中是经典自动空气制动：制动管压力降低时，各车控制阀把副风缸中的空气送入制动缸。现代动车组还可能用电信号指挥电空制动，并和再生制动混合。

</details>

**一起找：** 在博物馆隔着护栏找车厢间的空气软管；不触摸、不钻入连接处。""",

    102: """### 🔍 跟着捣固车看地下：钢轨下面藏着什么？

![有真实材质的轨道剖面，钢轨和混凝土轨枕位于碎石与地基上方](images/principles/generated/track-layers-cutaway.webp)

*写实剖面插图（AI 生成，不是实拍）：帮助看清轨道的上下层。· [生成说明](GENERATED_PRINCIPLE_IMAGES.md#track-layers-cutaway)*

先看大图：两条钢轨下面，还有轨枕、碎石和更厚的地基。

![钢轨、轨枕、道砟和地基逐层托住车轮的简图](images/principles/track-layers.svg)

车轮先压住钢轨。钢轨和轨枕把重量摊开。下面的碎石托住轨枕，还让雨水流走。更下面的地基把整条铁路稳稳撑住。

<details>
<summary>🔎 给大人再讲一点</summary>

有砟轨道由钢轨、扣件、轨枕、道砟和下部结构共同承载。板式轨道替代大部分道砟，却仍需要可靠基础、弹性部件和排水。生成图只展示一种常见概念层次，并非施工图。

</details>

**一起找：** 只从站台安全线内或照片比较：钢轨下面是碎石，还是一整块混凝土板？""",

    106: """### 🔍 看千叶单轨：倒挂的车挂在哪里？

刚才那张照片里，车厢在梁的下方，上方的轮子却看不见。

![悬挂式单轨的轮子藏在上方轨道梁内，连接架把车厢吊在下面](images/principles/suspended-monorail.svg)

千叶单轨把轮子藏在上面的轨道梁里。结实的连接架穿出梁底，把车厢吊住。它看起来飘在空中，其实仍是轮子在滚。

<details>
<summary>🔎 给大人再讲一点</summary>

图中讲的是千叶都市单轨采用的箱形梁内走行结构。悬挂铁路还有其他构造；它们通常都通过上方走行装置和悬吊构件把重量传给轨道。

</details>

**一起找：** 从安全位置找车厢和轨道之间那根结实的“脖子”。""",

    104: """### 🔍 看东京单轨：它怎样骑住一根梁？

刚才那张照片里，宽梁钻进了车身下面，像被列车骑住了。

![跨座式单轨剖面，承重轮在梁顶，导向轮贴着梁的两侧](images/principles/straddle-monorail.svg)

大橡胶轮在梁顶滚，托住车身。侧面的小轮抱住梁，帮列车转弯。乘客坐在更上面的车厢里，轮子藏在地板下面。

<details>
<summary>🔎 给大人再讲一点</summary>

竖向走行轮承担重量，横向导向轮提供侧向导向。换线时通常要移动或弯转一段较大的轨道梁，道岔和普通钢轨很不一样。

</details>

**一起找：** 在站台护栏内看，车身是不是把轨道梁顶面遮住了。""",

    110: """### 🔍 L0 什么时候用轮子，什么时候浮起来？

刚才那张照片里，L0 的车身跑在 U 形导轨中间。

![两格图显示 L0 低速时橡胶轮落下，高速时车侧磁铁与导轨侧壁线圈作用并留下空隙](images/principles/maglev.svg)

L0 慢慢走时，橡胶轮落下来。跑快以后，轮子收起来。车身两边的磁铁和侧边线圈把车托起，另一组线圈再推着它向前走。

<details>
<summary>🔎 给大人再讲一点</summary>

JR Central 的 SCMaglev 在约 150 km/h 以上收起低速橡胶轮，悬浮间隙约 10 cm；推进、悬浮和导向线圈均布置在导轨侧壁，导向力让列车保持在中间。Linimo、Transrapid 等磁浮系统的磁铁、间隙与低速支撑方式不同，不能套用这张 L0 图。

</details>

**一起找：** 看 L0 低速进站视频，找找车身下方有没有伸出的橡胶轮。""",

    138: """### 🔍 把胶轮转向架搬出来：一共有几种轮子？

![蒙特利尔地铁真实胶轮转向架，可见大承重轮与侧向小导向轮](images/principles/photos/p008-rubber-tyred-bogie.webp)

*实拍：胶轮地铁的转向架。不同城市会有不同构造。· [图片署名](PRINCIPLE_PHOTO_CREDITS.md#principle-photo-p008-rubber-tyred-bogie)*

先看真车：大橡胶轮托住车身，旁边还有小一些的导向轮。

![胶轮列车的大轮在平整走行面上滚，侧轮贴着导向面](images/principles/rubber-guideway.svg)

大橡胶轮在平整路面上滚。侧面的小轮贴着导向面，告诉车辆往哪里走。有的系统还留下钢轮和钢轨当帮手。

<details>
<summary>🔎 给大人再讲一点</summary>

橡胶轮胎常有较大黏着力，利于频繁加速和制动，但滚动阻力与发热也更大。不同系统的导向、回流和故障支撑办法不相同。

</details>

**一起找：** 在站台安全线内听一听，胶轮和钢轮的滚动声有什么不同。""",

    116: """### 🔍 真正的齿轨：中间那条“拉链”怎样咬住？

![真实齿轨铁路的齿轮与中央齿条相互啮合](images/principles/photos/p006-rack-pinion.webp)

*实拍：车底齿轮咬住轨道中央的齿条。· [图片署名](PRINCIPLE_PHOTO_CREDITS.md#principle-photo-p006-rack-pinion)*

先看真齿轨：圆齿轮的牙，正好塞进中间齿条的缝里。

![车底齿轮和轨道中央齿条一格一格啮合的图](images/principles/rack-rail.svg)

山坡太陡时，钢轮可能抓不稳。轨道中间就多了一条带牙齿的“拉链”。车底齿轮一格一格咬住它，帮列车爬山和下坡。

<details>
<summary>🔎 给大人再讲一点</summary>

普通铁路靠轮轨黏着传力；齿轮和齿条用几何啮合传力，也常参与下坡制动。不同齿轨系统的齿形并不相同。

</details>

**一起找：** 在照片里找两根普通钢轨中间有没有一条“拉链”。""",

    117: """### 🔍 两辆缆车：为什么总在半路遇见？

![斯堪森缆车的两辆真实车辆在坡道会车区段交会](images/principles/photos/p007-funicular-passing-loop.webp)

*实拍：两辆缆车正在中间的会车区交会。· [图片署名](PRINCIPLE_PHOTO_CREDITS.md#principle-photo-p007-funicular-passing-loop)*

先看真缆车：一辆在左边，一辆在右边，它们刚好在半山遇见。

![两辆缆索铁路车由同一套绳索连接，一辆上山一辆下山](images/principles/funicular-cable.svg)

两辆车常连在同一套缆索上。一辆上山，另一辆下山。它们在中间的会车区遇见，再继续去两头的车站。

<details>
<summary>🔎 给大人再讲一点</summary>

两车质量接近时能减少电动机需要克服的差额，但机器仍要克服摩擦、加速车辆并补偿乘客重量差。系统还配有工作制动和安全制动。

</details>

**一起找：** 从车站安全区或视频找找，两辆车是不是在坡道中间交会。""",
}


EXPECTED_LEARNING_CARDS = {
    4,
    5,
    8,
    20,
    32,
    52,
    56,
    69,
    75,
    80,
    83,
    100,
    101,
    102,
    104,
    106,
    110,
    116,
    117,
    124,
    127,
    129,
    138,
    159,
}

PRINCIPLE_SVG_RE = re.compile(
    r"!\[[^\n]*\]\(images/principles/[^)\n]+\.svg\)"
)


def validate_learning_blocks() -> None:
    """Fail early if a card anchor or single-principle block drifts."""
    actual_cards = set(LEARNING_BLOCKS_AFTER_CARD)
    if actual_cards != EXPECTED_LEARNING_CARDS:
        missing = sorted(EXPECTED_LEARNING_CARDS - actual_cards)
        extra = sorted(actual_cards - EXPECTED_LEARNING_CARDS)
        raise RuntimeError(
            f"integrated learning card mismatch; missing={missing}, extra={extra}"
        )

    for card, block in LEARNING_BLOCKS_AFTER_CARD.items():
        if block.count("### 🔍") != 1:
            raise RuntimeError(
                f"learning block after card {card:03d} must have exactly one heading"
            )
        if len(PRINCIPLE_SVG_RE.findall(block)) != 1:
            raise RuntimeError(
                f"learning block after card {card:03d} must have exactly one SVG"
            )
        if (
            block.count("<details>") != 1
            or block.count("</details>") != 1
            or block.count("<summary>🔎 给大人再讲一点</summary>") != 1
        ):
            raise RuntimeError(
                f"learning block after card {card:03d} must have one adult details"
            )
