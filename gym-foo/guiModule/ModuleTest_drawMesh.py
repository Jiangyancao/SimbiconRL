from . import guiBase
from . import drawMesh as dM
#from drawMesh import drawingMesh as DM

#import guiBase
#import drawMesh as dM

import wx
import sys
import os
import pydart2 as pydart
import numpy as np

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import cMat 
import SimbiconController as SC

from wx import glcanvas

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *


import pyassimp
from pyassimp.postprocess import *
from pyassimp.helper import *

import logging;logger = logging.getLogger("pyassimp_opengl")
logging.basicConfig(level= logging.INFO)

import quaternion


drawLimit = 10
#cameraP = ([3,3,3,0])

qrm = np.array([[1,0,0],
               [0,1,0],
               [0,0,1]])

gEye = np.array([3,3,3])
gAt = np.array([0,0,0])
gUp = np.array([0,1,0])



class dartGui(guiBase.GuiBase):
    def InitGL(self):
        self.cameraX = 0
        self.cameraY = 0
        self.cameraZ = 0
        self.xsubrad = 0
        self.ysubrad = 0
        self.Rxsubrad = 0
        self.Rysubrad = 0
        # set viewing projection
        glMatrixMode(GL_PROJECTION)
        #glFrustum(-0.5, 0.5, -0.5, 0.5, 1.0, 3.0)
        gluPerspective(60, 1, 1, 100)

        # position viewer
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self.myLookAt(np.array([3,3,3]), np.array([0,0,0]), np.array([0,1,0])) 
         
        #glTranslatef(0, 0, -1.0)
        #gluLookAt(np.radians(self.cameraX),np.radians(self.cameraY),np.radians(self.cameraZ),0,0,0,0,1,0)
        #gluLookAt(3,3,3,self.cameraX, self.cameraY, self.cameraZ, 0,1,0)
        # position object
        #glRotatef(self.y, 1.0, 0.0, 0.0)
        #glRotatef(self.x, 0.0, 1.0, 0.0)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        #glutTimerFunc(1000, self.Timer, 0)
        self.DMlist = list() 
        """
        for i in self.sim.skeletons[1].root_bodynode().shapenodes:
            tDM = DM()
            #print(i.shape.path())
            tDM.load_Model(i.shape.path(),None)
            self.DMlist.append(tDM)
            u[M`5&#self.DM.load_Model(i.shape.path(),None)
        """
        #glTranslatef(0,0,-2)
        self.recursive_load_ModelMeshes(self.sim.skeletons[0].root_bodynode())
        self.recursive_load_ModelMeshes(self.sim.skeletons[1].root_bodynode())
        self.sidx = 0
        self.drawCount = 0
        self.Rclicked = False
        self.Lclicked = False
        glutInit()

    def recursive_load_ModelMeshes(self,root):
        self.load_ModelMeshes(root)
        #input("recursive_load_ModelMeshes")
        for i in root.child_bodynodes:
            self.recursive_load_ModelMeshes(i)

    def load_ModelMeshes(self,bodyNodes):
        for i in bodyNodes.shapenodes:
            if(type(i.shape) is pydart.shape.MeshShape):
                tDM = dM.drawingMesh(0)
                tDM.load_Model(i.shape.path(),None)
                self.DMlist.append(tDM)
            elif(type(i.shape) is pydart.shape.BoxShape):
                tDM = dM.drawingMesh(1,i.shape.size())
                self.DMlist.append(tDM)
            else:
                input("type Error,, add new Shape Type")
    
    def recursive_draw_ModelMeshes(self,root):        
        #if self.sidx > drawLimit:
        #   return

        glPushMatrix()
        glMultMatrixd(np.transpose(root.relative_transform()))
        #glMultMatrixd(root.transform())
        #glMultMatrixf(np.transpose(root.world_transform()))
        
        
        self.draw_ModelMeshes(root)
        
        #glPopMatrix()
        for i in root.child_bodynodes:
            self.recursive_draw_ModelMeshes(i)

        glPopMatrix()

    def draw_ModelMeshes(self,bodyNodes):
        for i in bodyNodes.shapenodes:
            #print(i.shape.path())
            #input(len(bodyNodes.shapenodes))
            #glPushMatrix()
            #glMultMatrixf(np.transpose(i.relative_transform()))
            #input(i.relative_transform())
            if(type(i.shape) is pydart.shape.MeshShape):
                if '.stl' in i.shape.path():
                    self.DMlist[self.sidx].renders()
            #    self.sidx += 1
            #self.DMlist[self.sidx].renders()
            #elif(type(i.shape) is pydart.shape.BoxShape):
                #print("BOX")
            self.sidx += 1

            #glPopMatrix()

    def reset_sIdx(self):
        self.sidx = 0
 
    def OnDraw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(1.0,1.0,1.0,0)
        glPushMatrix()
        #print(self.cameraX)
        #print(self.cameraY)
        #print(self.cameraZ)
        self.drawGroundBox()
        self.recursive_draw_ModelMeshes(self.sim.skeletons[0].root_bodynode())
        self.recursive_draw_ModelMeshes(self.sim.skeletons[1].root_bodynode())
        self.reset_sIdx()
        #print("OnDrawEnd")
        glPopMatrix()
        self.SwapBuffers()

    def TimerFunc(self,):
        #print("TImer....")
        #self.controller.update()
        #self.sim.step()

        #glutPostRedisplay()
        #self.OnDraw()
        self.Refresh()

        return

    def OnMouseDown(self, event):
        #print(event.GetPosition())
        self.mouseDownPos = event.GetPosition()
        self.Lclicked = True 

    def OnMouseUp(self, event):
        #print(event.GetPosition())
        self.mouseUpPos = event.GetPosition()
        self.Lclicked = False
        #self.orbit()

    def orbit(self,):
        ysub = self.mouseUpPos[1] - self.mouseDownPos[1]
        ysub = (ysub/960)*45
        self.ysubrad = np.radians(ysub)

        xsub = self.mouseUpPos[0] - self.mouseDownPos[0]
        xsub = (xsub/1200)*45
        self.xsubrad = np.radians(xsub)
       
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        if np.absolute(ysub) >= np.absolute(xsub):
            self.updateEyeY()
        else:
            self.updateEyeX()
        self.myLookAt(gEye,gAt,gUp)


    def updateEyeY(self):
        global gEye, gAt, gUp
        wp = gEye - gAt
        w = wp/np.sqrt(np.dot(wp,wp))
        upt = np.cross(gUp,w)
        u = upt/np.sqrt(np.dot(upt,upt))
        v = np.cross(w,u)

        print(u)
        print(self.ysubrad)
    
        quat = quaternion.quaternion(np.cos(self.ysubrad),np.sin(self.ysubrad)*u[0],np.sin(self.ysubrad)*u[1],np.sin(self.ysubrad)*u[2])
        qrm = quaternion.as_rotation_matrix(quat)

        gEye = qrm @ wp + gAt
        #gEye = qrm @ gEye

    def updateEyeX(self):
        global gEye, gAt, gUp
        wp = gEye - gAt
        w = wp/np.sqrt(np.dot(wp,wp))
        upt = np.cross(gUp,w)
        u = upt/np.sqrt(np.dot(upt,upt))
        v = np.cross(w,u)

        print("vvvvv",v)
        print("xsubrad",self.xsubrad)
    
        quat = quaternion.quaternion(np.cos(self.xsubrad),np.sin(self.xsubrad)*gUp[0],np.sin(self.xsubrad)*gUp[1],np.sin(self.xsubrad)*gUp[2])
        qrm = quaternion.as_rotation_matrix(quat)

        gEye = qrm @ wp + gAt
        #gEye = qrm @ gEye
 


    def myLookAtRot(self,eye, at, up, Axis):     
        global qrm
        
        wp = eye - at
        w = wp/np.sqrt(np.dot(wp,wp))
        upt = np.cross(up,w)
        u = upt/np.sqrt(np.dot(upt,upt))
        v = np.cross(w,u)

        if Axis == 0:
            quat = quaternion.quaternion(np.cos(self.ysubrad),np.sin(self.ysubrad)*u[0],np.sin(self.ysubrad)*u[1],np.sin(self.ysubrad)*u[2])
            qrm = quaternion.as_rotation_matrix(quat) @ qrm
            rot = np.identity(4)
            rot[0,:3] = qrm[0]
            rot[1,:3] = qrm[1]
            rot[2,:3] = qrm[2]
        else:
            quat = quaternion.quaternion(np.cos(self.xsubrad),np.sin(self.xsubrad)*v[0],np.sin(self.xsubrad)*v[1],np.sin(self.xsubrad)*v[2])
            qrm = quaternion.as_rotation_matrix(quat) @ qrm
            rot = np.identity(4)
            rot[0,:3] = qrm[0]
            rot[1,:3] = qrm[1]
            rot[2,:3] = qrm[2]
 
        arr = np.identity(4)
        arr[0,:3] = u
        arr[1,:3] = v
        arr[2,:3] = w
        arr[0,3] = -np.dot(u,eye)
        arr[1,3] = -np.dot(v,eye)
        arr[2,3] = -np.dot(w,eye)
        #glMultMatrixf(np.transpose(arr))
                                                                    
        glMultMatrixf(np.transpose(arr))
        glMultMatrixf(rot)

    def myLookAt(self,eye, at, up):     
        wp = eye - at
        w = wp/np.sqrt(np.dot(wp,wp))
        upt = np.cross(up,w)
        u = upt/np.sqrt(np.dot(upt,upt))
        v = np.cross(w,u)

        arr = np.identity(4)
        arr[0,:3] = u
        arr[1,:3] = v
        arr[2,:3] = w
        arr[0,3] = -np.dot(u,eye)
        arr[1,3] = -np.dot(v,eye)
        arr[2,3] = -np.dot(w,eye)
                                                                   
        glMultMatrixf(np.transpose(arr))

    def OnRmouseDown(self,event):
        self.Rclicked = True
        self.rMouseDownPos = event.GetPosition()

    def OnRmouseUp(self,event):
        self.Rclicked = False
        self.rMouseUpPos = event.GetPosition()
        #self.pan()

    def pan(self,):
        self.rYsub = self.rMouseUpPos[1] - self.rMouseDownPos[1]
        self.rXsub = self.rMouseUpPos[0] - self.rMouseDownPos[0]
      
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self.updateEye_At()
         
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self.myLookAt(gEye,gAt,gUp)

    def updateEye_At(self):
        global gEye, gAt, gUp
        wp = gEye - gAt
        w = wp/np.sqrt(np.dot(wp,wp))
        upt = np.cross(gUp,w)
        u = upt/np.sqrt(np.dot(upt,upt))
        v = np.cross(w,u)       
        
        gEye = gEye - u*self.rXsub/100 + v*self.rYsub/100
        gAt = gAt - u*self.rXsub/100 + v*self.rYsub/100

    def OnMouseWheel(self, event):
        #print(event.GetWheelRotation())
        #print(event.GetWheelDelta())
        #input("look")
        self.zoomI = event.GetWheelRotation()/2880
        self.updateEye_zoom()
 
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self.myLookAt(gEye,gAt,gUp)



    def updateEye_zoom(self):
        global gEye, gAt, gUp
        vect = gAt - gEye
        #print(gEye)
        gEye = gEye + self.zoomI * vect
        #input(gEye)

    def OnKeyDown(self, event):
        code = event.GetKeyCode()
        if code == 65:
            #self.cameraX = (self.cameraX + 80)%90
            self.cameraX = self.cameraX - 0.01
        elif code == 68:
            #self.cameraX = (self.cameraX + 10)%90
            self.cameraX = self.cameraX + 0.01
        elif code == 87:
            #self.cameraY = (self.cameraY + 10)%90
            self.cameraY = self.cameraY + 0.01
        elif code == 83:
            #self.cameraY = (self.cameraY + 80)%90
            self.cameraY = self.cameraY - 0.01
        elif code == 82:
            #self.cameraZ = (self.cameraZ + 10)%90
            self.cameraZ = self.cameraZ + 0.01
        elif code == 70:
            #self.cameraZ = (self.cameraZ + 80)%90
            self.cameraZ = self.cameraZ - 0.01
        else:
            print(code)

        #glLoadIdentity()
        #glMatrixMode(GL_MODELVIEW)
        #glLoadIdentity()
        #gluLookAt(np.radians(self.cameraX),np.radians(self.cameraY),np.radians(self.cameraZ),0,0,0,0,1,0)
        #gluLookAt(3,3,3,self.cameraX,self.cameraY,self.cameraZ,0,1,0)

    def mouseMotion(self, event):
        #print(event.GetPosition())
        if self.Lclicked == True:
            self.mouseUpPos = event.GetPosition()
            self.orbit()
            self.mouseDownPos = self.mouseUpPos
        elif self.Rclicked == True:
            self.rMouseUpPos = event.GetPosition()
            self.pan()
            self.rMouseDownPos = self.rMouseUpPos

    def drawGroundBox(self,):
        glPushMatrix()
        glTranslatef(0.0,-1.5,0.0)
        glColor3f(1.0,1.0,0.0)
        glEnable(GL_COLOR_MATERIAL)
        glutSolidCube(1.0)
        glDisable(GL_COLOR_MATERIAL)
        glPopMatrix()

skel_path = "/home/qfei/dart/data/sdf/atlas/"

if __name__ == '__main__':
    pydart.init()

    world = pydart.World(1/1000)


    ground = world.add_skeleton(skel_path+"ground.urdf")
    atlas = world.add_skeleton(skel_path+"atlas_v3_no_head_soft_feet.sdf");

    skel = world.skeletons[1]

    q = skel.q
    q[0] = -0.5*np.pi
    q[4] = q[4]+0.01
    skel.set_positions(q)

    controller = SC.Controller(skel,world)

    app = wx.App(0)

    frame = wx.Frame(None, -1, size=(1200,960))
    #gui = dartGui(frame,world,controller)
    gui = dartGui(frame,world,controller)
    frame.Show(True)

    app.MainLoop()
    print("end") 
