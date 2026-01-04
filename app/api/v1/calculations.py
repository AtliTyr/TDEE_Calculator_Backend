from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.calculation import Calculation
from app.models.user import User
from app.schemas.calculation import (
    CalculationCreate,
    CalculationResponse,
    CalculationHistoryResponse,
    CalculationStatsResponse,
    CalculationStats
)

router = APIRouter()


@router.post(
    "/",
    response_model=CalculationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый расчет",
    description="Создание нового расчета для текущего пользователя. Сохраняет входные данные и результаты расчета."
)
async def create_calculation(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    calculation_in: CalculationCreate
):
    """
    Создать новый расчет для текущего пользователя
    
    Пример тела запроса:
    {
      "goal_id": 1,
      "input_data": {
        "weight": 70.5,
        "height": 175.0,
        "age": 30,
        "gender": "male",
        "activity_level": "moderate",
        "activity_level_id": 3,
        "goal": "loss"
      },
      "results": {
        "bmr": 1665,
        "tdee": 2581,
        "calorie_target": 2065,
        "coefficient": 1.55,
        "formula_used": "mifflin_st_jeor"
      }
    }
    """
    try:
        # Валидация входных данных
        input_data = calculation_in.input_data
        
        # Проверяем обязательные поля во входных данных
        required_fields = ['weight', 'height', 'age', 'gender', 'activity_level']
        for field in required_fields:
            if field not in input_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Отсутствует обязательное поле в input_data: {field}"
                )
        
        # Проверяем результаты
        results = calculation_in.results
        required_results = ['bmr', 'tdee', 'calorie_target']
        for field in required_results:
            if field not in results:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Отсутствует обязательное поле в results: {field}"
                )
        
        # Проверяем goal_id
        if calculation_in.goal_id not in [1, 2, 3]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Некорректный goal_id. Допустимые значения: 1 (похудеть), 2 (поддерживать), 3 (набрать)"
            )
        
        # Создаем новый расчет
        calculation = Calculation(
            user_id=current_user.id,
            goal_id=calculation_in.goal_id.value if hasattr(calculation_in.goal_id, 'value') else calculation_in.goal_id,
            input_data=calculation_in.input_data,
            results=calculation_in.results,
            created_at=datetime.utcnow()
        )
        
        db.add(calculation)
        await db.commit()
        await db.refresh(calculation)
        
        # Логируем успешное создание
        print(f"Создан новый расчет для пользователя {current_user.id}: {calculation.id}")
        
        return calculation
        
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        print(f"Ошибка при создании расчета: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании расчета: {str(e)}"
        )

@router.get(
    "/",
    response_model=CalculationHistoryResponse,
    summary="Получить историю расчетов пользователя",
    description="Получение истории расчетов текущего пользователя с фильтрацией по времени"
)
async def get_calculations(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    days: Optional[int] = Query(None, gt=0, le=365, description="Фильтр по последним N дням"),
    limit: int = Query(100, gt=0, le=1000, description="Лимит записей (макс. 1000)"),
    offset: int = Query(0, ge=0, description="Смещение для пагинации")
):
    """
    Получить историю расчетов пользователя
    
    Возвращает только расчеты текущего авторизованного пользователя.
    Можно отфильтровать по периоду (дни) и использовать пагинацию.
    
    - **days**: фильтрация по последним N дням (опционально)
    - **limit**: количество записей (по умолчанию 100, максимум 1000)
    - **offset**: смещение для пагинации
    """
    try:
        # Базовый запрос для текущего пользователя
        query = select(Calculation).where(Calculation.user_id == current_user.id)
        
        # Применяем фильтр по времени, если указан
        if days is not None:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            query = query.where(Calculation.created_at >= cutoff_date)
        
        # Считаем общее количество для пагинации
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query)
        
        # Получаем данные с сортировкой (новые сначала) и пагинацией
        query = query.order_by(desc(Calculation.created_at))
        query = query.offset(offset).limit(limit)
        
        result = await db.execute(query)
        calculations = result.scalars().all()
        
        return {
            "calculations": calculations,
            "total": total
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении истории расчетов: {str(e)}"
        )


@router.get(
    "/{calculation_id}",
    response_model=CalculationResponse,
    summary="Получить расчет по ID",
    description="Получение конкретного расчета пользователя по его идентификатору"
)
async def get_calculation(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    calculation_id: UUID
):
    """
    Получить расчет по ID
    
    Пользователь может получить только свой расчет.
    Требуется авторизация.
    """
    try:
        # Ищем расчет с проверкой владельца
        query = select(Calculation).where(
            (Calculation.id == calculation_id) &
            (Calculation.user_id == current_user.id)  # Проверяем, что расчет принадлежит пользователю
        )
        
        result = await db.execute(query)
        calculation = result.scalar_one_or_none()
        
        if not calculation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Расчет не найден или у вас нет к нему доступа"
            )
        
        return calculation
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении расчета: {str(e)}"
        )


@router.delete(
    "/{calculation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить расчет",
    description="Удаление расчета пользователя по ID"
)
async def delete_calculation(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    calculation_id: UUID
):
    """
    Удалить расчет по ID
    
    Пользователь может удалить только свой расчет.
    Требуется авторизация.
    """
    try:
        # Ищем расчет с проверкой владельца
        query = select(Calculation).where(
            (Calculation.id == calculation_id) &
            (Calculation.user_id == current_user.id)  # Проверяем, что расчет принадлежит пользователю
        )
        
        result = await db.execute(query)
        calculation = result.scalar_one_or_none()
        
        if not calculation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Расчет не найден или у вас нет прав на его удаление"
            )
        
        # Удаляем расчет
        await db.delete(calculation)
        await db.commit()
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при удалении расчета: {str(e)}"
        )


@router.get(
    "/recent/latest",
    response_model=CalculationResponse,
    summary="Получить последний расчет",
    description="Получение самого последнего расчета пользователя"
)
async def get_latest_calculation(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Получить самый последний расчет пользователя
    
    Возвращает самый свежий расчет по дате создания.
    Требуется авторизация.
    """
    try:
        query = select(Calculation).where(
            Calculation.user_id == current_user.id
        ).order_by(desc(Calculation.created_at)).limit(1)
        
        result = await db.execute(query)
        calculation = result.scalar_one_or_none()
        
        if not calculation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="У вас пока нет расчетов"
            )
        
        return calculation
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении последнего расчета: {str(e)}"
        )
    
@router.get(
    "/stats/summary",
    response_model=CalculationStatsResponse,
    summary="Статистика расчетов пользователя",
    description="Получение статистики по всем расчетам пользователя"
)
async def get_calculations_stats(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Получить статистику по расчетам пользователя"""
    try:
        # Общее количество расчетов
        total_query = select(func.count()).where(Calculation.user_id == current_user.id)
        total = await db.scalar(total_query) or 0
        
        # Расчеты за последние 7 дней
        week_ago = datetime.utcnow() - timedelta(days=7)
        last_7_days_query = select(func.count()).where(
            (Calculation.user_id == current_user.id) &
            (Calculation.created_at >= week_ago)
        )
        last_7_days = await db.scalar(last_7_days_query) or 0
        
        # Расчеты за последние 30 дней
        month_ago = datetime.utcnow() - timedelta(days=30)
        last_30_days_query = select(func.count()).where(
            (Calculation.user_id == current_user.id) &
            (Calculation.created_at >= month_ago)
        )
        last_30_days = await db.scalar(last_30_days_query) or 0
        
        # Получаем последний расчет
        latest_query = select(Calculation).where(
            Calculation.user_id == current_user.id
        ).order_by(desc(Calculation.created_at)).limit(1)
        
        result = await db.execute(latest_query)
        latest_calculation = result.scalar_one_or_none()
        
        # Статистика по калориям (если есть расчеты)
        avg_calories = None
        if total > 0:
            avg_query = select(func.avg(Calculation.results['calorie_target'].as_float())).where(
                Calculation.user_id == current_user.id
            )
            avg_result = await db.scalar(avg_query)
            avg_calories = round(float(avg_result), 1) if avg_result else None
        
        # Самая частая цель
        most_common_goal = None
        if total > 0:
            # Получаем цель из последнего расчета
            if latest_calculation:
                goal_id = latest_calculation.goal_id
                goal_names = {
                    1: "Похудеть",
                    2: "Поддерживать",
                    3: "Набрать"
                }
                most_common_goal = goal_names.get(goal_id, "Неизвестно")
        
        stats = CalculationStats(
            total_calculations=total,
            last_7_days=last_7_days,
            last_30_days=last_30_days,
            average_calories=avg_calories,
            most_common_goal=most_common_goal
        )
        
        return {
            "stats": stats,
            "last_calculation": latest_calculation
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении статистики: {str(e)}"
        )