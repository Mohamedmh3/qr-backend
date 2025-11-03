"""
Django management command to create comprehensive test data.
Usage: python manage.py create_test_data
"""

from django.core.management.base import BaseCommand
from users.models import User, Team, Game, GameResult
from django.utils import timezone
import random
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Creates test data for API testing'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing test data before creating new data',
        )
    
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('  CREATING TEST DATA'))
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))
        
        # Clear existing test data if requested
        if kwargs.get('clear'):
            self.stdout.write('Clearing existing test data...')
            try:
                GameResult.objects.all().delete()
                self.stdout.write(self.style.SUCCESS('✓ Deleted all game results'))
                
                Team.objects.all().delete()
                self.stdout.write(self.style.SUCCESS('✓ Deleted all teams'))
                
                Game.objects.all().delete()
                self.stdout.write(self.style.SUCCESS('✓ Deleted all games'))
                
                User.objects.filter(email__contains='@example.com').delete()
                self.stdout.write(self.style.SUCCESS('✓ Deleted test users\n'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error clearing data: {e}'))
        
        # Create test users
        self.stdout.write(self.style.WARNING('Creating Users...'))
        users = []
        
        for i in range(1, 4):
            try:
                user, created = User.objects.get_or_create(
                    email=f'testuser{i}@example.com',
                    defaults={
                        'name': f'Test User {i}',
                        'role': 'user',
                        'is_active': True,
                    }
                )
                if created:
                    user.set_password('TestPass123!')
                    user.save()
                    self.stdout.write(self.style.SUCCESS(
                        f'✓ Created user: {user.email} (QR: {user.qr_id})'
                    ))
                else:
                    self.stdout.write(f'  ⚠ User already exists: {user.email}')
                users.append(user)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating user {i}: {e}'))
        
        # Create admin user
        try:
            admin, created = User.objects.get_or_create(
                email='admin@example.com',
                defaults={
                    'name': 'Admin User',
                    'role': 'admin',
                    'is_staff': True,
                    'is_superuser': True,
                    'is_active': True,
                }
            )
            if created:
                admin.set_password('AdminPass123!')
                admin.save()
                self.stdout.write(self.style.SUCCESS(
                    f'✓ Created admin: {admin.email} (QR: {admin.qr_id})'
                ))
            else:
                self.stdout.write(f'  ⚠ Admin already exists: {admin.email}')
            users.insert(0, admin)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating admin: {e}'))
        
        # Create games
        self.stdout.write('\n' + self.style.WARNING('Creating Games...'))
        games_data = [
            {
                'name': 'Basketball',
                'description': 'Outdoor basketball game',
                'max_points': 100,
                'min_points': 0
            },
            {
                'name': 'Soccer',
                'description': 'Team soccer match',
                'max_points': 10,
                'min_points': 0
            },
            {
                'name': 'Chess',
                'description': 'Strategic board game',
                'max_points': 1,
                'min_points': 0
            },
            {
                'name': 'Tennis',
                'description': 'Doubles tennis match',
                'max_points': 50,
                'min_points': 0
            },
            {
                'name': 'Volleyball',
                'description': 'Beach volleyball',
                'max_points': 25,
                'min_points': 0
            },
        ]
        
        games = []
        for game_data in games_data:
            try:
                game, created = Game.objects.get_or_create(
                    game_name=game_data['name'],
                    defaults={
                        'game_description': game_data['description'],
                        'max_points': game_data['max_points'],
                        'min_points': game_data['min_points'],
                        'is_active': True,
                    }
                )
                games.append(game)
                if created:
                    self.stdout.write(self.style.SUCCESS(
                        f'✓ Created game: {game.game_name} (ID: {game.game_id}, Max: {game.max_points})'
                    ))
                else:
                    self.stdout.write(f'  ⚠ Game already exists: {game.game_name}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating game {game_data["name"]}: {e}'))
        
        # Create teams for each user
        self.stdout.write('\n' + self.style.WARNING('Creating Teams...'))
        teams = []
        team_names = ['Warriors', 'Champions', 'Legends', 'Titans', 'Phoenix']
        
        for user in users[1:]:  # Skip admin
            for i in range(2):
                try:
                    team, created = Team.objects.get_or_create(
                        team_name=f'{user.name} - {team_names[i]}',
                        user=user,
                        defaults={'is_active': True}
                    )
                    teams.append(team)
                    if created:
                        self.stdout.write(self.style.SUCCESS(
                            f'✓ Created team: {team.team_name} (ID: {team.team_id})'
                        ))
                    else:
                        self.stdout.write(f'  ⚠ Team already exists: {team.team_name}')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f'Error creating team for {user.name}: {e}'
                    ))
        
        # Create game results
        self.stdout.write('\n' + self.style.WARNING('Creating Game Results...'))
        results_created = 0
        
        for team in teams:
            # Each team plays 2-4 games
            num_games = random.randint(2, 4)
            selected_games = random.sample(games, k=min(num_games, len(games)))
            
            for game in selected_games:
                try:
                    # Generate score between min and max
                    points = random.randint(game.min_points, game.max_points)
                    verified = random.choice([True, False])
                    
                    result, created = GameResult.objects.get_or_create(
                        user=team.user,
                        team=team,
                        game=game,
                        defaults={
                            'points_scored': points,
                            'notes': f'Test game played on {timezone.now().date()}',
                            'verified_by_admin': verified,
                            'admin_user': users[0] if verified else None,  # Admin verifies
                        }
                    )
                    
                    if created:
                        results_created += 1
                        status = '✓ Verified' if verified else '○ Unverified'
                        self.stdout.write(self.style.SUCCESS(
                            f'{status} Result: {team.team_name} - {game.game_name}: {points} pts'
                        ))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f'Error creating result for {team.team_name}: {e}'
                    ))
        
        # Print summary
        self.stdout.write('\n' + self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('  TEST DATA CREATED SUCCESSFULLY'))
        self.stdout.write(self.style.SUCCESS('='*60))
        
        self.stdout.write(f'\n{self.style.WARNING("DATABASE SUMMARY:")}')
        self.stdout.write(f'  Total Users: {User.objects.count()}')
        self.stdout.write(f'  Total Games: {Game.objects.count()}')
        self.stdout.write(f'  Total Teams: {Team.objects.count()}')
        self.stdout.write(f'  Total Results: {GameResult.objects.count()}')
        
        self.stdout.write(f'\n{self.style.WARNING("TEST CREDENTIALS:")}')
        self.stdout.write('  Admin:')
        self.stdout.write('    Email: admin@example.com')
        self.stdout.write('    Password: AdminPass123!')
        self.stdout.write('\n  Regular Users:')
        self.stdout.write('    testuser1@example.com / TestPass123!')
        self.stdout.write('    testuser2@example.com / TestPass123!')
        self.stdout.write('    testuser3@example.com / TestPass123!')
        
        self.stdout.write('\n' + self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('  Ready for testing!'))
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))
