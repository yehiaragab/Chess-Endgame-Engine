


import numpy as np
from degree_freedom_king1 import *
from degree_freedom_king2 import *
from degree_freedom_queen import *
from generate_game import *


class Chess_Env:
    
    def __init__(self,N_grid):
        
        
        self.N_grid=N_grid                     # SIZE OF THE BOARD
        
        self.Board=np.zeros([N_grid,N_grid])   # THE BOARD, THIS WILL BE FILLED BY 0 (NO PIECE), 1 (AGENT'S KING), 2 (AGENT'S QUEEN), 3 (OPPONENT'S KING)
        
        self.p_k1=np.zeros([2,1])              # POSITION OF THE AGENT'S KING AS COORDINATES
        self.p_k2=np.zeros([2,1])              # POSITION OF THE OPPOENT'S KING AS COORDINATES
        self.p_q1=np.zeros([2,1])              # POSITION OF THE AGENT'S QUEEN AS COORDINATES
        
        self.dfk1=np.zeros([N_grid,N_grid])    # ALL POSSIBLE ACTIONS FOR THE AGENT'S KING (LOCATIONS WHERE IT CAN MOVE WITHOUT THE PRESENCE OF THE OTHER PIECES)
        self.dfk2=np.zeros([N_grid,N_grid])    # ALL POSSIBLE ACTIONS FOR THE OPPONENT'S KING (LOCATIONS WHERE IT CAN MOVE WITHOUT THE PRESENCE OF THE OTHER PIECES)
        self.dfq1=np.zeros([N_grid,N_grid])    # ALL POSSIBLE ACTIONS FOR THE AGENT'S QUEEN (LOCATIONS WHERE IT CAN MOVE WITHOUT THE PRESENCE OF THE OTHER PIECES)
        
        self.dfk1_constrain=np.zeros([N_grid,N_grid])  # ALLOWED ACTIONS FOR THE AGENT'S KING CONSIDERING ALSO THE OTHER PIECES
        self.dfk2_constrain=np.zeros([N_grid,N_grid])  # ALLOWED ACTIONS FOT THE OPPONENT'S KING CONSIDERING ALSO THE OTHER PIECES
        self.dfq1_constrain=np.zeros([N_grid,N_grid])  # ALLOWED ACTIONS FOT THE AGENT'S QUEEN CONSIDERING ALSO THE OTHER PIECES
        
        self.ak1=np.zeros([8])                         # ALLOWED ACTIONS OF THE AGENT'S KING (CONSIDERING OTHER PIECES), ONE-HOT ENCODED
        self.possible_king_a=np.shape(self.ak1)[0]     # TOTAL NUMBER OF POSSIBLE ACTIONS FOR AGENT'S KING
        
        self.aq1=np.zeros([8*(self.N_grid-1)])         # ALLOWED ACTIONS OF THE AGENT'S QUEEN (CONSIDERING OTHER PIECES), ONE-HOT ENCODED
        self.possible_queen_a=np.shape(self.aq1)[0]     # TOTAL NUMBER OF POSSIBLE ACTIONS FOR AGENT'S QUEEN
        
        self.check=0                                   # 1 (0) IF ENEMY KING (NOT) IN CHECK
        
        # THIS MAP IS USEFUL FOR US TO UNDERSTAND THE DIRECTION OF MOVEMENT GIVEN THE ACTION MADE (SKIP...)
        self.map=np.array([[1, 0],
                            [-1, 0],
                            [0, 1],
                            [0, -1],
                            [1, 1],
                            [1, -1],
                            [-1, 1],
                            [-1, -1]])

        
        
    def Initialise_game(self):
        
        
        # START THE GAME BY SETTING PIECIES
        
        self.Board,self.p_k2,self.p_k1,self.p_q1=generate_game(self.N_grid)

        self.Board, self.p_k1, self.p_k2, self.p_q1 = self.rotate_board(self.Board, self.p_k1, self.p_k2, self.p_q1, k2=False)
       
        # Allowed actions for the agent's king
        self.dfk1_constrain, self.a_k1, self.dfk1 = degree_freedom_king1(self.p_k1, self.p_k2, self.p_q1, self.Board)
        
        # Allowed actions for the agent's queen
        self.dfq1_constrain, self.a_q1, self.dfq1  = degree_freedom_queen(self.p_k1, self.p_k2, self.p_q1, self.Board)
        
        # Allowed actions for the enemy's king
        self.dfk2_constrain, self.a_k2, self.check = degree_freedom_king2(self.dfk1, self.p_k2, self.dfq1, self.Board, self.p_k1)
        
        # ALLOWED ACTIONS FOR THE AGENT, ONE-HOT ENCODED
        allowed_a=np.concatenate([self.a_q1,self.a_k1],0)
        
        # FEATURES (INPUT TO NN) AT THIS POSITION
        X=self.Features()

        
        
        return self.Board, X, allowed_a
        
    
    def OneStep(self,a_agent):
        
        # SET REWARD TO ZERO IF GAME IS NOT ENDED
        R=0
        # SET Done TO ZERO (GAME NOT ENDED)
        Done=0
        
        
        # PERFORM THE AGENT'S ACTION ON THE CHESS BOARD
        
        if a_agent < self.possible_queen_a:    # THE AGENT MOVED ITS QUEEN 
           
           # UPDATE QUEEN'S POSITION
           direction = int(np.ceil((a_agent + 1) / (self.N_grid - 1))) - 1
           steps = a_agent - direction * (self.N_grid - 1) + 1

           self.Board[self.p_q1[0], self.p_q1[1]] = 0
           
           mov = self.map[direction, :] * steps
           self.Board[self.p_q1[0] + mov[0], self.p_q1[1] + mov[1]] = 2
           self.p_q1[0] = self.p_q1[0] + mov[0]
           self.p_q1[1] = self.p_q1[1] + mov[1]

        else:                                 # THE AGENT MOVED ITS KING                               
           
           # UPDATE KING'S POSITION
           direction = a_agent - self.possible_queen_a
           steps = 1

           self.Board[self.p_k1[0], self.p_k1[1]] = 0
           mov = self.map[direction, :] * steps
           self.Board[self.p_k1[0] + mov[0], self.p_k1[1] + mov[1]] = 1
           self.p_k1[0] = self.p_k1[0] + mov[0]
           self.p_k1[1] = self.p_k1[1] + mov[1]

        
        self.Board, self.p_k1, self.p_k2, self.p_q1 = self.rotate_board(self.Board, self.p_k1, self.p_k2, self.p_q1, k2=False)

        # COMPUTE THE ALLOWED ACTIONS AFTER AGENT'S ACTION
        # Allowed actions for the agent's king
        self.dfk1_constrain, self.a_k1, self.dfk1 = degree_freedom_king1(self.p_k1, self.p_k2, self.p_q1, self.Board)
        
        # Allowed actions for the agent's queen
        self.dfq1_constrain, self.a_q1, self.dfq1  = degree_freedom_queen(self.p_k1, self.p_k2, self.p_q1, self.Board)
        
        # Allowed actions for the enemy's king
        self.dfk2_constrain, self.a_k2, self.check = degree_freedom_king2(self.dfk1, self.p_k2, self.dfq1, self.Board, self.p_k1)

        
        # CHECK IF POSITION IS A CHECMATE, DRAW, OR THE GAME CONTINUES
        
        # CASE OF CHECKMATE
        if np.sum(self.dfk2_constrain) == 0 and self.dfq1[self.p_k2[0], self.p_k2[1]] == 1:
           
            # King 2 has no freedom and it is checked
            # Checkmate and collect reward
            Done = 1       # The epsiode ends
            R = 1          # Reward for checkmate
            allowed_a=[]   # Allowed_a set to nothing (end of the episode)
            X=np.zeros(37)           # Features set to nothing (end of the episode)
        
        # CASE OF DRAW
        elif np.sum(self.dfk2_constrain) == 0 and self.dfq1[self.p_k2[0], self.p_k2[1]] == 0:
           
            # King 2 has no freedom but it is not checked
            Done = 1        # The epsiode ends
            R = 0.       # Reward for draw
            allowed_a=[]    # Allowed_a set to nothing (end of the episode)
            X=np.zeros(37)             # Features set to nothing (end of the episode)
        
        # THE GAME CONTINUES
        else:
            
            # THE OPPONENT MOVES THE KING IN A RANDOM SAFE LOCATION
            allowed_enemy_a = np.where(self.a_k2 > 0)[0]
            a_help = int(np.ceil(np.random.rand() * allowed_enemy_a.shape[0]) - 1)
            a_enemy = allowed_enemy_a[a_help]

            direction = a_enemy
            steps = 1

            self.Board[self.p_k2[0], self.p_k2[1]] = 0
            mov = self.map[direction, :] * steps
            self.Board[self.p_k2[0] + mov[0], self.p_k2[1] + mov[1]] = 3

            self.p_k2[0] = self.p_k2[0] + mov[0]
            self.p_k2[1] = self.p_k2[1] + mov[1]
            
            self.Board, self.p_k1, self.p_k2, self.p_q1 = self.rotate_board(self.Board, self.p_k1, self.p_k2, self.p_q1, k2=True)
            
            # COMPUTE THE ALLOWED ACTIONS AFTER THE OPPONENT'S ACTION
            # Possible actions of the King
            self.dfk1_constrain, self.a_k1, self.dfk1 = degree_freedom_king1(self.p_k1, self.p_k2, self.p_q1, self.Board)
            
            # Allowed actions for the agent's king
            self.dfq1_constrain, self.a_q1, self.dfq1  = degree_freedom_queen(self.p_k1, self.p_k2, self.p_q1, self.Board)
            
            # Allowed actions for the enemy's king
            self.dfk2_constrain, self.a_k2, self.check = degree_freedom_king2(self.dfk1, self.p_k2, self.dfq1, self.Board, self.p_k1)

            # ALLOWED ACTIONS FOR THE AGENT, ONE-HOT ENCODED
            allowed_a=np.concatenate([self.a_q1,self.a_k1],0)
            # FEATURES
            X=self.Features()
        
        return self.Board, X, allowed_a, R, Done
        
        
    # DEFINITION OF THE FEATURES (SEE ALSO ASSIGNMENT DESCRIPTION)
    def Features(self):
        
        
        s_k1 = np.array(self.Board[0:2,0:2] == 1).astype(float).reshape(-1)   # FEATURES FOR KING POSITION
        s_q1 = np.array(self.Board == 2).astype(float).reshape(-1)   # FEATURES FOR QUEEN POSITION
        s_k2 = np.array(self.Board[0:3,2:4] == 3).astype(float).reshape(-1)   # FEATURE FOR ENEMY'S KING POSITION
        s_k2 = np.concatenate([s_k2, np.array(self.Board[3][3] == 3).astype(float).reshape(-1)])

        x = np.concatenate([s_k1, s_q1, s_k2],0)

        # s_k1 = np.array(self.Board == 1).astype(float).reshape(-1)   # FEATURES FOR KING POSITION
        # s_q1 = np.array(self.Board == 2).astype(float).reshape(-1)   # FEATURES FOR QUEEN POSITION
        # s_k2 = np.array(self.Board == 3).astype(float).reshape(-1)   # FEATURE FOR ENEMY'S KING POSITION
        
        # check=np.zeros([2])    # CHECK? FEATURE
        # check[self.check]=1   
        
        # K2dof=np.zeros([8])   # NUMBER OF ALLOWED ACTIONS FOR ENEMY'S KING, ONE-HOT ENCODED
        # K2dof[np.sum(self.dfk2_constrain).astype(int)]=1
        
        # # ALL FEATURES...
        # x = np.concatenate([s_k1, s_q1, s_k2, check, K2dof],0)

        return x
        
    def rotate_board(self, Board, p_k1, p_k2, p_q1, k2=False):
        """
        The coordinates of the board are as follows:
        [
        [(0,0),(0,1),(0,2),(0,3)],
        [(1,0),(1,1),(1,2),(1,3)],
        [(2,0),(2,1),(2,2),(2,3)],
        [(3,0),(3,1)(3,2),(3,3)]
        ]

        c1 is the first quarter of the board [0:2][0:2], 
        c2 as the second quarter [0:2][2:4], 
        c3 as the third quarter [2:4][0:2],
        c4 as the fourth quarter [2:4][2:4].

        h1 is defined as [0:3][2:4] + (3,3)

        k1 will always be in one of the 4 quarters of the board ck1, 
        while k2 will always be in a different quarter of the board ck2
        because there's at least 1 square separating k1 and k2. 
        The goal of the function is to rotate the board so that k1 is in c1,
        and so that k2 is in h1. This is done to reduce the number of possible states,
        as all the pieces can move in all directions.

        The k2 parameter is true if only k2 has moved since the last rotation. 
        """

        if not k2:
            if p_k1[1] >= 2:
                # k1 isn't in c1
                if p_k1[0] < 2:
                    # k1 is in c2
                    Board = np.rot90(Board, 1)
                else:
                    # k1 is in c4
                    Board = np.rot90(Board, 2)
            elif p_k1[0] >= 2:
                # k1 is in c3
                Board = np.rot90(Board, 3)
        
        p_k2 = np.array(np.where(Board==3)).reshape(2,)

        if p_k2[1] < 2 or (p_k2[1] == 2 and p_k2[0] == 3):
            # k2 isn't in h1
            Board = Board.T
            p_k2 = np.array(np.where(Board==3)).reshape(2,)

        p_k1 = np.array(np.where(Board==1)).reshape(2,)
        p_q1 = np.array(np.where(Board==2)).reshape(2,)

        return Board, p_k1, p_k2, p_q1