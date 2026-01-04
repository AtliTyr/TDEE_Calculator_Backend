from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import BaseModel, Field, validator, model_validator
from enum import Enum


class GoalEnum(int, Enum):
    """Enum для целей расчета"""
    CUT = 1      # Похудеть
    MAINTAIN = 2 # Поддерживать
    BULK = 3     # Набрать


class GenderEnum(str, Enum):
    """Enum для пола"""
    MALE = "male"
    FEMALE = "female"


class ActivityLevelEnum(str, Enum):
    """Enum для уровня активности"""
    SEDENTARY = "sedentary"
    LIGHT = "light"
    MODERATE = "moderate"
    HIGH = "high"
    EXTREME = "extreme"


class CalculationInputData(BaseModel):
    """Схема для входных данных расчета"""
    weight: float = Field(..., gt=0, le=500, description="Вес в кг")
    height: float = Field(..., gt=0, le=300, description="Рост в см")
    age: int = Field(..., gt=0, le=120, description="Возраст")
    gender: GenderEnum = Field(..., description="Пол")
    activity_level: ActivityLevelEnum = Field(..., description="Уровень активности")
    activity_level_id: int = Field(..., ge=1, le=5, description="ID уровня активности")
    goal: str = Field(..., description="Цель (loss/maintain/gain)")


class CalculationResults(BaseModel):
    """Схема для результатов расчета"""
    bmr: int = Field(..., ge=0, description="Основной обмен веществ (ккал)")
    tdee: int = Field(..., ge=0, description="Суточный расход энергии (ккал)")
    calorie_target: int = Field(..., ge=0, description="Целевые калории")
    coefficient: float = Field(..., ge=1.0, le=2.0, description="Коэффициент активности")
    formula_used: str = Field(default="mifflin_st_jeor", description="Используемая формула")


class CalculationBase(BaseModel):
    """Базовая схема для вычислений"""
    goal_id: GoalEnum = Field(..., description="ID цели расчета (1-3)")
    input_data: Dict[str, Any] = Field(..., description="Входные данные для расчета")
    results: Dict[str, Any] = Field(..., description="Результаты расчета")
    
    @model_validator(mode='after')
    def validate_data_consistency(self):
        """Проверка согласованности данных"""
        # Можно добавить дополнительные проверки
        # Например, что goal_id соответствует goal в input_data
        return self


class CalculationCreate(CalculationBase):
    """Схема для создания нового вычисления"""
    pass


class CalculationResponse(CalculationBase):
    """Схема для ответа с информацией о вычислении"""
    id: UUID
    user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class CalculationHistoryResponse(BaseModel):
    """Схема для ответа с историей вычислений"""
    calculations: List[CalculationResponse]
    total: int
    period: Optional[str] = Field(None, description="Период выборки")


class CalculationStats(BaseModel):
    """Схема для статистики расчетов"""
    total_calculations: int = Field(0, description="Всего расчетов")
    last_7_days: int = Field(0, description="Расчетов за 7 дней")
    last_30_days: int = Field(0, description="Расчетов за 30 дней")
    average_calories: Optional[float] = Field(None, description="Среднее значение калорий")
    most_common_goal: Optional[str] = Field(None, description="Самая частая цель")


class CalculationStatsResponse(BaseModel):
    """Схема для ответа со статистикой"""
    stats: CalculationStats
    last_calculation: Optional[CalculationResponse] = Field(None, description="Последний расчет")