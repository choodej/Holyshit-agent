"""Base Port — interface กลางที่ adapter ทุกตัวต้องบอก "ฉันคือใคร"

ใช้ให้ graphify/ตัวตรวจสุขภาพระบบรู้ว่าแต่ละ adapter เสียบเข้ากับ port ไหน
"""
from __future__ import annotations

from abc import ABC, abstractmethod


class Port(ABC):
    """ทุก adapter implement Port เพื่อรายงานตัวเองได้"""

    @property
    @abstractmethod
    def port_name(self) -> str:
        """ชื่อ port ที่ adapter นี้ทำหน้าที่ (เช่น 'Logger', 'MemberRepository')"""
        raise NotImplementedError
