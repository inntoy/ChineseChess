

class ChessValue:
    RedValue = {
    # 将(帅)
    'King' : [
      [0,  0,  0, 11, 15, 11,  0,  0,  0],  
      [0,  0,  0,  2,  2,  2,  0,  0,  0],  
      [0,  0,  0,  1,  1,  1,  0,  0,  0],  
      [0,  0,  0,  0,  0,  0,  0,  0,  0],  
      [0,  0,  0,  0,  0,  0,  0,  0,  0],  
      [0,  0,  0,  0,  0,  0,  0,  0,  0],  
      [0,  0,  0,  0,  0,  0,  0,  0,  0],  
      [0,  0,  0,  0,  0,  0,  0,  0,  0],  
      [0,  0,  0,  0,  0,  0,  0,  0,  0],  
      [0,  0,  0,  0,  0,  0,  0,  0,  0]
        ],
    # 士(仕)
    'Guard' : [
      [0,  0,  0, 20,  0, 20,  0,  0,  0],
      [0,  0,  0,  0, 23,  0,  0,  0,  0],
      [0,  0,  0, 20,  0, 20,  0,  0,  0],  
      [0,  0,  0,  0,  0,  0,  0,  0,  0],  
      [0,  0,  0,  0,  0,  0,  0,  0,  0],  
      [0,  0,  0,  0,  0,  0,  0,  0,  0],  
      [0,  0,  0,  0,  0,  0,  0,  0,  0],
      [0,  0,  0,  0,  0,  0,  0,  0,  0],  
      [0,  0,  0,  0,  0,  0,  0,  0,  0],  
      [0,  0,  0,  0,  0,  0,  0,  0,  0]
    ], 
    # 象(相)
    'Bishop':[
      [0,  0, 20,  0,  0,  0, 20,  0,  0],
      [0,  0,  0,  0,  0,  0,  0,  0,  0],
      [18, 0,  0,  0, 23,  0,  0,  0, 18],
      [0,  0,  0,  0,  0,  0,  0,  0,  0],
      [0,  0, 20,  0,  0,  0, 20,  0,  0],
      [0,  0,  0,  0,  0,  0,  0,  0,  0],
      [0,  0,  0,  0,  0,  0,  0,  0,  0],
      [0,  0,  0,  0,  0,  0,  0,  0,  0],
      [0,  0,  0,  0,  0,  0,  0,  0,  0],
      [0,  0,  0,  0,  0,  0,  0,  0,  0]
    ],
    # 马
    'Knight':[
      [88, 85, 90, 88, 90, 88, 90, 85, 88],
      [85, 90, 92, 93, 78, 93, 92, 90, 85],
      [93, 92, 94, 95, 92, 95, 94, 92, 93],
      [92, 94, 98, 95, 98, 95, 98, 94, 92],
      [90, 98,101,102,103,102,101, 98, 90],
      [90,100, 99,103,104,103, 99,100, 90],
      [93,108,100,107,100,107,100,108, 93],
      [92, 98, 99,103, 99,103, 99, 98, 92],
      [90, 96,103, 97, 94, 97,103, 96, 90],
      [90, 90, 90, 96, 90, 96, 90, 90, 90]
    ],
    # 车
    'Rock':[
      [194,206,204,212,200,212,204,206,194],
      [200,208,206,212,200,212,206,208,200],
      [198,208,204,212,212,212,204,208,198],
      [204,209,204,212,214,212,204,209,204],
      [208,212,212,214,215,214,212,212,208],
      [208,211,211,214,215,214,211,211,208],
      [206,213,213,216,216,216,213,213,206],
      [206,208,207,214,216,214,207,208,206],
      [206,212,209,216,233,216,209,212,206],
      [206,208,207,213,214,213,207,208,206]
    ],
    # 炮
    'Cannon':[
      [ 96, 96, 97, 99, 99, 99, 97, 96, 96],
      [ 96, 97, 98, 98, 98, 98, 98, 97, 96],
      [ 97, 96,100, 99,101, 99,100, 96, 97],
      [ 96, 96, 96, 96, 96, 96, 96, 96, 96],
      [ 95, 96, 99, 96,100, 96, 99, 96, 95],
      [ 96, 96, 96, 96,100, 96, 96, 96, 96],
      [ 96, 99, 99, 98,100, 98, 99, 99, 96],
      [ 97, 97, 96, 91, 92, 91, 96, 97, 97],
      [ 98, 98, 96, 92, 89, 92, 96, 98, 98],
      [100,100, 96, 91, 90, 91, 96,100,100],
    ],
    # 卒(兵)
    'Pawn':[
      [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
      [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
      [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
      [ 7,  0,  7,  0, 15,  0,  7,  0,  7],
      [ 7,  0, 13,  0, 16,  0, 13,  0,  7],
      [14, 18, 20, 27, 29, 27, 20, 18, 14],
      [19, 23, 27, 29, 30, 29, 27, 23, 19],
      [19, 24, 32, 37, 37, 37, 32, 24, 19],
      [19, 24, 34, 42, 44, 42, 34, 24, 19],
      [ 9,  9,  9, 11, 13, 11,  9,  9,  9],
    ]
    }


    BlackValue = {
    # 将(帅)
    'King' : [
      [0,  0,  0,  0,  0,  0,  0,  0,  0],  
      [0,  0,  0,  0,  0,  0,  0,  0,  0],  
      [0,  0,  0,  0,  0,  0,  0,  0,  0],  
      [0,  0,  0,  0,  0,  0,  0,  0,  0],  
      [0,  0,  0,  0,  0,  0,  0,  0,  0],  
      [0,  0,  0,  0,  0,  0,  0,  0,  0],  
      [0,  0,  0,  0,  0,  0,  0,  0,  0],  
      [0,  0,  0,  1,  1,  1,  0,  0,  0],  
      [0,  0,  0,  2,  2,  2,  0,  0,  0],  
      [0,  0,  0, 11, 15, 11,  0,  0,  0]
        ],
    # 士(仕)
    'Guard' : [
      [0,  0,  0,  0,  0,  0,  0,  0,  0],  
      [0,  0,  0,  0,  0,  0,  0,  0,  0],  
      [0,  0,  0,  0,  0,  0,  0,  0,  0],  
      [0,  0,  0,  0,  0,  0,  0,  0,  0],  
      [0,  0,  0,  0,  0,  0,  0,  0,  0],  
      [0,  0,  0,  0,  0,  0,  0,  0,  0],  
      [0,  0,  0,  0,  0,  0,  0,  0,  0],
      [0,  0,  0, 20,  0, 20,  0,  0,  0],
      [0,  0,  0,  0, 23,  0,  0,  0,  0],
      [0,  0,  0, 20,  0, 20,  0,  0,  0]
    ], 
    # 象(相)
    'Bishop':[
      [0,  0,  0,  0,  0,  0,  0,  0,  0],
      [0,  0,  0,  0,  0,  0,  0,  0,  0],
      [0,  0,  0,  0,  0,  0,  0,  0,  0],
      [0,  0,  0,  0,  0,  0,  0,  0,  0],
      [0,  0,  0,  0,  0,  0,  0,  0,  0],
      [0,  0, 20,  0,  0,  0, 20,  0,  0],
      [0,  0,  0,  0,  0,  0,  0,  0,  0],
      [18, 0,  0,  0, 23,  0,  0,  0, 18],
      [0,  0,  0,  0,  0,  0,  0,  0,  0],
      [0,  0, 20,  0,  0,  0, 20,  0,  0]
    ],
    # 马
    'Knight':[
      [90, 90, 90, 96, 90, 96, 90, 90, 90],
      [90, 96,103, 97, 94, 97,103, 96, 90],
      [92, 98, 99,103, 99,103, 99, 98, 92],
      [93,108,100,107,100,107,100,108, 93],
      [90,100, 99,103,104,103, 99,100, 90],
      [90, 98,101,102,103,102,101, 98, 90],
      [92, 94, 98, 95, 98, 95, 98, 94, 92],
      [93, 92, 94, 95, 92, 95, 94, 92, 93],
      [85, 90, 92, 93, 78, 93, 92, 90, 85],
      [88, 85, 90, 88, 90, 88, 90, 85, 88]
    ],
    # 车
    'Rock':[
      [206,208,207,213,214,213,207,208,206],
      [206,212,209,216,233,216,209,212,206],
      [206,208,207,214,216,214,207,208,206],
      [206,213,213,216,216,216,213,213,206],
      [208,211,211,214,215,214,211,211,208],
      [208,212,212,214,215,214,212,212,208],
      [204,209,204,212,214,212,204,209,204],
      [198,208,204,212,212,212,204,208,198],
      [200,208,206,212,200,212,206,208,200],
      [194,206,204,212,200,212,204,206,194]
    ],
    # 炮
    'Cannon':[
      [100,100, 96, 91, 90, 91, 96,100,100],
      [ 98, 98, 96, 92, 89, 92, 96, 98, 98],
      [ 97, 97, 96, 91, 92, 91, 96, 97, 97],
      [ 96, 99, 99, 98,100, 98, 99, 99, 96],
      [ 96, 96, 96, 96,100, 96, 96, 96, 96],
      [ 95, 96, 99, 96,100, 96, 99, 96, 95],
      [ 96, 96, 96, 96, 96, 96, 96, 96, 96],
      [ 97, 96,100, 99,101, 99,100, 96, 97],
      [ 96, 97, 98, 98, 98, 98, 98, 97, 96],
      [ 96, 96, 97, 99, 99, 99, 97, 96, 96]
    ],
    # 卒(兵)
    'Pawn':[
      [ 9,  9,  9, 11, 13, 11,  9,  9,  9],
      [19, 24, 34, 42, 44, 42, 34, 24, 19],
      [19, 24, 32, 37, 37, 37, 32, 24, 19],
      [19, 23, 27, 29, 30, 29, 27, 23, 19],
      [14, 18, 20, 27, 29, 27, 20, 18, 14],
      [ 7,  0, 13,  0, 16,  0, 13,  0,  7],
      [ 7,  0,  7,  0, 15,  0,  7,  0,  7],
      [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
      [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
      [ 0,  0,  0,  0,  0,  0,  0,  0,  0]
    ]
    }