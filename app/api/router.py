from fastapi import APIRouter
from app.api.endpoints import financial, scenarios, auth, spreadsheets

api_router = APIRouter()

# Incluir rotas de diferentes módulos
api_router.include_router(auth.router, prefix="/auth", tags=["Autenticação"])
api_router.include_router(spreadsheets.router, prefix="/spreadsheets", tags=["Planilhas"])
api_router.include_router(scenarios.router, prefix="/scenarios", tags=["Cenários"])
api_router.include_router(financial.router, prefix="/financial", tags=["Financial"]) 