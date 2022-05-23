# 中国象棋人机对弈网站

## 食用方法

在当前文件夹下打开终端，输入`python3 -m serv/`可以运行一个服务器，然后在浏览器上输入并打开网址127.0.0.1:8000，就可以下棋了。红方为玩家，黑方为电脑。

电脑默认的搜索时间为8秒（一般会严重超过这个时间），如果嫌下棋速度太慢，可以在web/py_lib/auto_chess2.py文件夹里找到auto_move函数，找到`board_explore = BoardExplore(board, 8)`，这里的第二个值“8”就是搜索时间，单位是秒。一般来说，时间越长电脑越“聪明”。不过现在棋力还不如中等难度的电脑。

***建议每下完一盘ctrl+c关闭终端里的程序，然后再打开，否则可能会爆内存！！！***



## 参考文献

------

参考文章-象棋巫师：https://www.xqbase.com/computer.htm

象棋wiki(Chess Programming wiki)：https://www.chessprogramming.org/Main_Page

np问题：http://www.matrix67.com/blog/archives/105



## 搜索方法

______
alphabeta剪枝法：

    wiki(没有使用负值传递)：https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning

pvs(主要変例搜索，alphabeta的变种)法：

    [建议看这个]象棋wiki(使用了负值传递的方法): https://www.chessprogramming.org/Principal_Variation_Search 
    CSDN(没有使用负值传递): https://blog.csdn.net/u012501320/article/details/25081933
    象棋巫师(使用了负值传递)：https://www.xqbase.com/computer/advanced_pvs.htm

蒙特卡洛搜索树：

    知乎：https://zhuanlan.zhihu.com/p/333348915
    B站视频：https://www.bilibili.com/video/BV1fY4y1876L/?spm_id_from=333.788.recommend_more_video.-1

评估函数的设计：https://www.xqbase.com/computer/evalue_intro1.htm

置换表：https://www.xqbase.com/computer/search_hashing.htm

置换表中胜利条件的设置：https://www.xqbase.com/computer/other_winning.htm



## 对下法进行排序

_____
由于alpha-beta，pvs等搜索方法要求比较好的着法的顺序(即前几个着法就可以得到本节点的界限值)，因此需要对着法进行排序。着法排序的方式也称为启发式。

静态启发搜索：吃子的着法大概率比不吃子的好，这里使用Mvv/Lva(最有价值受害者/最小没价值攻击者，Most Valuable Victim/Least Valuable Attacker)的评估方法对所有吃子着法进行评估

动态启发搜索：    
1. 使用置换表，置换表的键是棋盘的局面和下棋方，值是当前局面下之前搜索得到的最优着法以及探索深度(或者说是搜索树的高度，叶子节点为0)。
2. 使用兄弟节点(同深度)的最优着法，这里我们只存处两个
3. 使用历史表，历史表里只存储了每种情况下的最好着法，值是得到这个着法时的节点的搜索深度的平方(或者说是搜索树的高度，叶子节点为0)



## 避免水平线效应

_____
如果搜索深度是固定的，那么到达搜索深度后进行评分往往得不到准确的值，甚至有可能会得到错误的分数。例如搜索到最后一层时，假如此时有被将军或者其他棋子有被抓到的情况，此时对棋盘进行评分会得到一个错误的值（评分只统计局面上棋子的子力）。这种情况被称为水平线效应。为了避免这种情况，一般会用几种方法让搜索深度动态变化（只会变得更深）。

1. 将军延伸：每次得到下法后，都会检查下棋方是否被将军，如果被将军，就会让搜索增加一层。
2. 静态搜索：当搜索深度为0后，进入静态搜索。静态搜索首先判断是否被将军。如果被将军，就生成所有的下法；如果没有被将军，就先进行评分看看能否截断，然后再按Mvv/Lva的顺序生成所有吃子的下法。然后再对每一种下法进行搜索。
3. 空着前向搜索

由于将军延伸和静态搜索在长将解将时会永远搜索下去，因此需要引入重复局面判断和最大搜索深度的限制。



## TODO(咕)

------

1. 评价函数可能还是比较简陋，可以再复杂一点。
2. 蒙特卡洛搜索树，强化学习
3. 一些象棋的规则（六次长将判负，六次棋局重复则判和）。
4. 开局表和残局表。



## BUG

------

1. 由于置换表和历史表里的项太多，内存占用巨大(3-4GB)；
2. 运行速度太慢；
3. 残局时由于将军延伸导致每步的搜索往往都要到最大搜索深度，因此有些情况下搜索时间非常长（可能有5-6分钟）。