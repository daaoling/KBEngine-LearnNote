# -*- coding: utf-8 -*-
# import KBEngine
from BaseApp import KBEngine
import random
import SCDefine
import time
import GlobalConst
import d_spaces
import d_avatar_inittab
from KBEDebug import *
from interfaces.GameObject import GameObject
from interfaces.Teleport import Teleport

class Avatar(KBEngine.Proxy,
			GameObject,
			Teleport):
	"""
	角色实体
	"""
	def __init__(self):
		KBEngine.Proxy.__init__(self)
		GameObject.__init__(self)
		Teleport.__init__(self)
		
		self.accountEntity = None
		self.cellData["dbid"] = self.databaseID
		self.nameB = self.cellData["name"]
		self.spaceUTypeB = self.cellData["spaceUType"]
		
		self._destroyTimer = 0

	def onEntitiesEnabled(self):
		"""
		KBEngine method.
		该entity被正式激活为可使用， 此时entity已经建立了client对应实体， 可以在此创建它的
		cell部分。
		"""
		INFO_MSG("Avatar[%i-%s] entities enable. spaceUTypeB=%s, mailbox:%s" % (self.id, self.nameB, self.spaceUTypeB, self.client))
		Teleport.onEntitiesEnabled(self)
		
	def onGetCell(self):
		"""
		KBEngine method.
		entity的cell部分实体被创建成功
		"""
		DEBUG_MSG('Avatar::onGetCell: %s' % self.cell)
		
	def createCell(self, space):
		"""
		defined method.
		创建cell实体
		"""
		self.createCellEntity(space)
	
	def destroySelf(self):
		"""
		"""
		if self.client is not None:
			return
			
		if self.cell is not None:
			# 销毁cell实体
			self.destroyCellEntity()
			return
			
		# 如果帐号ENTITY存在 则也通知销毁它
		if self.accountEntity != None:
			if time.time() - self.accountEntity.relogin > 1:
				self.accountEntity.activeCharacter = None
				self.accountEntity.destroy()
				self.accountEntity = None
			else:
				DEBUG_MSG("Avatar[%i].destroySelf: relogin =%i" % (self.id, time.time() - self.accountEntity.relogin))
				
		# 销毁base
		self.destroy()

	def onClientDeath(self):
		"""
		KBEngine method.
		entity丢失了客户端实体
		"""
		DEBUG_MSG("Avatar[%i].onClientDeath:" % self.id)
		# 防止正在请求创建cell的同时客户端断开了， 我们延时一段时间来执行销毁cell直到销毁base
		# 这段时间内客户端短连接登录则会激活entity
		self._destroyTimer = self.addTimer(1, 0, SCDefine.TIMER_TYPE_DESTROY)
			
	def onClientGetCell(self):
		"""
		KBEngine method.
		客户端已经获得了cell部分实体的相关数据
		"""
		INFO_MSG("Avatar[%i].onClientGetCell:%s" % (self.id, self.client))
		
	def onDestroyTimer(self, tid, tno):
		DEBUG_MSG("Avatar::onDestroyTimer: %i, tid:%i, arg:%i" % (self.id, tid, tno))
		self.destroySelf()

Avatar._timermap = {}
Avatar._timermap.update(GameObject._timermap)
Avatar._timermap.update(Teleport._timermap)
Avatar._timermap[SCDefine.TIMER_TYPE_DESTROY] = Avatar.onDestroyTimer

