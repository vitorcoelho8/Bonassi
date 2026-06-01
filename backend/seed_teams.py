from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import or_, select
from sqlalchemy.exc import SQLAlchemyError


BACKEND_DIR = Path(__file__).resolve().parent
load_dotenv(BACKEND_DIR / ".env")

from app.database import db
from app.main import create_app
from app.teams.models import Team


# Fonte: FIFA, "Qualified teams for the FIFA World Cup 2026" e "Final Draw results".
# A estrutura abaixo privilegia manutencao simples caso nomes/codigos sejam ajustados.
RAW_TEAMS = (
    {"name": "México", "normalized_name": "mexico", "fifa_code": "MEX", "group_name": "A", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "África do Sul", "normalized_name": "africa do sul", "fifa_code": "RSA", "group_name": "A", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "Coreia do Sul", "normalized_name": "coreia do sul", "fifa_code": "KOR", "group_name": "A", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "Tchéquia", "normalized_name": "tchequia", "fifa_code": "CZE", "group_name": "A", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "Canadá", "normalized_name": "canada", "fifa_code": "CAN", "group_name": "B", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "Bósnia e Herzegovina", "normalized_name": "bosnia e herzegovina", "fifa_code": "BIH", "group_name": "B", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "Catar", "normalized_name": "catar", "fifa_code": "QAT", "group_name": "B", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "Suíça", "normalized_name": "suica", "fifa_code": "SUI", "group_name": "B", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "Brasil", "normalized_name": "brasil", "fifa_code": "BRA", "group_name": "C", "is_brazil": True, "is_confirmed": True, "is_active": True},
    {"name": "Marrocos", "normalized_name": "marrocos", "fifa_code": "MAR", "group_name": "C", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "Haiti", "normalized_name": "haiti", "fifa_code": "HAI", "group_name": "C", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "Escócia", "normalized_name": "escocia", "fifa_code": "SCO", "group_name": "C", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "Estados Unidos", "normalized_name": "estados unidos", "fifa_code": "USA", "group_name": "D", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "Paraguai", "normalized_name": "paraguai", "fifa_code": "PAR", "group_name": "D", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "Austrália", "normalized_name": "australia", "fifa_code": "AUS", "group_name": "D", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "Turquia", "normalized_name": "turquia", "fifa_code": "TUR", "group_name": "D", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "Alemanha", "normalized_name": "alemanha", "fifa_code": "GER", "group_name": "E", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "Curaçao", "normalized_name": "curacao", "fifa_code": "CUW", "group_name": "E", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "Costa do Marfim", "normalized_name": "costa do marfim", "fifa_code": "CIV", "group_name": "E", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "Equador", "normalized_name": "equador", "fifa_code": "ECU", "group_name": "E", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "Holanda", "normalized_name": "holanda", "fifa_code": "NED", "group_name": "F", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "Japão", "normalized_name": "japao", "fifa_code": "JPN", "group_name": "F", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "Suécia", "normalized_name": "suecia", "fifa_code": "SWE", "group_name": "F", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "Tunísia", "normalized_name": "tunisia", "fifa_code": "TUN", "group_name": "F", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "Bélgica", "normalized_name": "belgica", "fifa_code": "BEL", "group_name": "G", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "Egito", "normalized_name": "egito", "fifa_code": "EGY", "group_name": "G", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "Irã", "normalized_name": "ira", "fifa_code": "IRN", "group_name": "G", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "Nova Zelândia", "normalized_name": "nova zelandia", "fifa_code": "NZL", "group_name": "G", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "Espanha", "normalized_name": "espanha", "fifa_code": "ESP", "group_name": "H", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "Cabo Verde", "normalized_name": "cabo verde", "fifa_code": "CPV", "group_name": "H", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "Arábia Saudita", "normalized_name": "arabia saudita", "fifa_code": "KSA", "group_name": "H", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "Uruguai", "normalized_name": "uruguai", "fifa_code": "URU", "group_name": "H", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "França", "normalized_name": "franca", "fifa_code": "FRA", "group_name": "I", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "Senegal", "normalized_name": "senegal", "fifa_code": "SEN", "group_name": "I", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "Iraque", "normalized_name": "iraque", "fifa_code": "IRQ", "group_name": "I", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "Noruega", "normalized_name": "noruega", "fifa_code": "NOR", "group_name": "I", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "Argentina", "normalized_name": "argentina", "fifa_code": "ARG", "group_name": "J", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "Argélia", "normalized_name": "argelia", "fifa_code": "ALG", "group_name": "J", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "Áustria", "normalized_name": "austria", "fifa_code": "AUT", "group_name": "J", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "Jordânia", "normalized_name": "jordania", "fifa_code": "JOR", "group_name": "J", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "Portugal", "normalized_name": "portugal", "fifa_code": "POR", "group_name": "K", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "RD Congo", "normalized_name": "rd congo", "fifa_code": "COD", "group_name": "K", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "Uzbequistão", "normalized_name": "uzbequistao", "fifa_code": "UZB", "group_name": "K", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "Colômbia", "normalized_name": "colombia", "fifa_code": "COL", "group_name": "K", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "Inglaterra", "normalized_name": "inglaterra", "fifa_code": "ENG", "group_name": "L", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "Croácia", "normalized_name": "croacia", "fifa_code": "CRO", "group_name": "L", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "Gana", "normalized_name": "gana", "fifa_code": "GHA", "group_name": "L", "is_brazil": False, "is_confirmed": True, "is_active": True},
    {"name": "Panamá", "normalized_name": "panama", "fifa_code": "PAN", "group_name": "L", "is_brazil": False, "is_confirmed": True, "is_active": True},
)


# Arquivos verificados em frontend/img/Bandeiras com extensao .jpg.
FLAG_FILES = {
    "africa do sul": "Africa_do_Sul.jpg",
    "alemanha": "Alemanha.jpg",
    "arabia saudita": "Arabia_Saudita.jpg",
    "argelia": "Argelia.jpg",
    "argentina": "Argentina.jpg",
    "australia": "Australia.jpg",
    "austria": "Austria.jpg",
    "belgica": "Belgica.jpg",
    "bosnia e herzegovina": "Bosnia_e_Herzegovina.jpg",
    "brasil": "Brasil.jpg",
    "cabo verde": "Cabo_Verde.jpg",
    "canada": "Canada.jpg",
    "catar": "Catar.jpg",
    "colombia": "Colombia.jpg",
    "coreia do sul": "Coreia_do_Sul.jpg",
    "costa do marfim": "Costa_do_Marfim.jpg",
    "croacia": "Croacia.jpg",
    "curacao": "Curacao.jpg",
    "egito": "Egito.jpg",
    "equador": "Equador.jpg",
    "escocia": "Escocia.jpg",
    "espanha": "Espanha.jpg",
    "estados unidos": "Estados_Unidos.jpg",
    "franca": "Franca.jpg",
    "gana": "Gana.jpg",
    "haiti": "Haiti.jpg",
    "holanda": "Holanda.jpg",
    "inglaterra": "Inglaterra.jpg",
    "ira": "Ira.jpg",
    "iraque": "Iraque.jpg",
    "japao": "Japao.jpg",
    "jordania": "Jordania.jpg",
    "marrocos": "Marrocos.jpg",
    "mexico": "Mexico.jpg",
    "noruega": "Noruega.jpg",
    "nova zelandia": "Nova_Zelandia.jpg",
    "panama": "Panama.jpg",
    "paraguai": "Paraguai.jpg",
    "portugal": "Portugal.jpg",
    "rd congo": "RD_Congo.jpg",
    "senegal": "Senegal.jpg",
    "suecia": "Suecia.jpg",
    "suica": "Suica.jpg",
    "tchequia": "Republica_Tcheca.jpg",
    "tunisia": "Tunisia.jpg",
    "turquia": "Turquia.jpg",
    "uruguai": "Uruguai.jpg",
    "uzbequistao": "Uzbequistao.jpg",
}


def with_flag_url(team_data: dict) -> dict:
    filename = FLAG_FILES.get(team_data["normalized_name"])
    return {
        **team_data,
        "flag_url": f"/img/Bandeiras/{filename}" if filename else None,
    }


TEAMS = tuple(with_flag_url(team_data) for team_data in RAW_TEAMS)


def find_existing_team(team_data: dict) -> Team | None:
    filters = [Team.normalized_name == team_data["normalized_name"]]
    if team_data.get("fifa_code"):
        filters.append(Team.fifa_code == team_data["fifa_code"])

    stmt = select(Team).where(or_(*filters))
    return db.session.execute(stmt).scalars().first()


def update_team(team: Team, team_data: dict) -> bool:
    changed = False
    for field, value in team_data.items():
        if getattr(team, field) != value:
            setattr(team, field, value)
            changed = True
    return changed


def seed_teams() -> None:
    print("Inserindo selecoes da Copa 2026...")

    for team_data in TEAMS:
        existing_team = find_existing_team(team_data)
        if existing_team:
            if update_team(existing_team, team_data):
                print(f"[*] Atualizado: {team_data['name']}")
            else:
                print(f"[=] Ja existe: {team_data['name']}")
            continue

        db.session.add(Team(**team_data))
        print(f"[+] Criado: {team_data['name']}")

    db.session.commit()
    print("Seed concluido com sucesso!")


def main() -> None:
    app = create_app()
    with app.app_context():
        try:
            seed_teams()
        except SQLAlchemyError as error:
            db.session.rollback()
            print(f"Erro ao executar seed: {error}")
            raise SystemExit(1) from error


if __name__ == "__main__":
    main()
