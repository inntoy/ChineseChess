# 中国象棋人机对弈网站

参考文章-象棋巫师：https://www.xqbase.com/computer.htm

象棋wiki(Chess Programming wiki)：https://www.chessprogramming.org/Main_Page

np问题：http://www.matrix67.com/blog/archives/105

## 搜索法
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


## 启发式搜索
_____
由于alpha-beta，pvs等搜索方法要求比较好的着法的顺序(即前几个着法就可以得到本节点的界限值)，因此需要对着法进行排序。着法排序的方式也称为启发式。

静态启发搜索：吃子的着法大概率比不吃子的好，这里使用MVV/LVA(最有价值受害者/最小没价值攻击者，Most Valuable Victim/Least Valuable Attacker)的评估方法对所有吃子着法进行评估

动态启发搜索：    
1. 使用置换表，置换表的键是棋盘的局面和下棋方，值是当前局面下之前搜索得到的最优着法以及探索深度(或者说是搜索树的高度，叶子节点为0)。
2. 使用兄弟节点(同深度)的最优着法，这里我们只存处两个
3. 使用历史表，历史表里只存储了每种情况下的最好着法，值是得到这个着法时的节点的搜索深度(或者说是搜索树的高度，叶子节点为0)

## 避免水平线效应
_____
在到达搜索深度后，继续进行搜索，但只搜索吃子的着法，同时