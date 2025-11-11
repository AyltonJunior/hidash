"""
Migração para truncar descrições de dashboards para máximo de 100 caracteres
"""
from app import app, db
from models import Dashboard

def truncate_dashboard_descriptions():
    """Truncar descrições de dashboards para o limite máximo de 100 caracteres"""
    with app.app_context():
        # Buscar todos os dashboards
        dashboards = Dashboard.query.all()
        
        # Contador para acompanhamento
        updated_count = 0
        
        # Iterar sobre cada dashboard e truncar descrições longas
        for dashboard in dashboards:
            if dashboard.description and len(dashboard.description) > 100:
                print(f"Truncando descrição do dashboard '{dashboard.name}'")
                print(f"  Original ({len(dashboard.description)} caracteres): {dashboard.description}")
                
                # Truncar para 97 caracteres e adicionar "..."
                dashboard.description = dashboard.description[:97] + "..."
                
                print(f"  Nova ({len(dashboard.description)} caracteres): {dashboard.description}")
                updated_count += 1
        
        # Commit das alterações se houver dashboards atualizados
        if updated_count > 0:
            print(f"Total de {updated_count} descrições de dashboards truncadas")
            db.session.commit()
            print("Alterações salvas com sucesso!")
        else:
            print("Nenhuma descrição precisou ser truncada")

if __name__ == "__main__":
    truncate_dashboard_descriptions()