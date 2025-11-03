"""
Seed script to populate mock data for Team/Game/GameResult and an admin user.
Safe for djongo: uses simple create/filter operations and try/except.
Run with: venv\Scripts\python seed_gaming_mock_data.py
"""

import os
import django
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qr_access_backend.settings')
django.setup()

from django.db import transaction
from users.models import User, Team, Game, GameResult

logger = logging.getLogger(__name__)


def get_or_create_admin():
    admin_email = 'admin@example.com'
    admin_name = 'Admin User'
    admin_password = 'AdminPass123!'
    admin = User.objects.filter(email=admin_email).first()
    if not admin:
        admin = User.objects.create_superuser(email=admin_email, name=admin_name, password=admin_password)
        logger.info('Created admin user')
    else:
        logger.info('Admin user already exists')
    return admin


def get_or_create_user():
    user_email = 'player1@example.com'
    user_name = 'Player One'
    user_password = 'TestPass123!'
    user = User.objects.filter(email=user_email).first()
    if not user:
        user = User.objects.create_user(email=user_email, name=user_name, password=user_password)
        logger.info('Created regular user')
    else:
        logger.info('Regular user already exists')
    return user


def seed_games():
    games_data = [
        dict(game_id='GAME-RUNNER', game_name='Endless Runner', game_description='Run and collect coins', max_points=500, min_points=0),
        dict(game_id='GAME-QUIZ', game_name='Trivia Quiz', game_description='Answer questions', max_points=100, min_points=0),
        dict(game_id='GAME-PUZZLE', game_name='Puzzle Mania', game_description='Solve puzzles', max_points=300, min_points=0),
    ]
    created = []
    for gd in games_data:
        game = Game.objects.filter(game_id=gd['game_id']).first()
        if not game:
            game = Game.objects.create(**gd)
            logger.info(f"Created game {gd['game_id']}")
        created.append(game)
    return created


def seed_team_for_user(user: User):
    team = Team.objects.filter(team_name='Alpha Team', user=user).first()
    if not team:
        import uuid
        team = Team.objects.create(
            team_id=f"TEAM-{uuid.uuid4().hex[:8].upper()}",
            team_name='Alpha Team',
            user=user,
        )
        logger.info('Created team Alpha Team')
    else:
        logger.info('Team Alpha Team already exists')
    return team


def seed_results(user: User, team: Team, games: list[Game]):
    import random
    for game in games:
        existing = GameResult.objects.filter(user=user, team=team, game=game).first()
        if existing:
            continue
        import uuid
        points = random.randint(game.min_points, game.max_points)
        GameResult.objects.create(
            result_id=f"RESULT-{uuid.uuid4().hex[:8].upper()}",
            user=user,
            team=team,
            game=game,
            points_scored=points,
            notes=f"Auto-seeded score for {game.game_name}",
        )
        logger.info(f"Seeded result for {game.game_name}: {points} pts")


def main():
    try:
        with transaction.atomic():
            admin = get_or_create_admin()
            user = get_or_create_user()
            games = seed_games()
            team = seed_team_for_user(user)
            seed_results(user, team, games)
        print('Seeding completed successfully.')
    except Exception as e:
        logger.error(f'Seeding failed: {e}')
        print('Seeding failed. Check logs for details.')


if __name__ == '__main__':
    main()






