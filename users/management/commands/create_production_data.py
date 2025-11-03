"""
Django management command to create production-ready mock data.
Usage: python manage.py create_production_data [--clear]
"""

from django.core.management.base import BaseCommand
from users.models import User, Team, Game, GameResult
from django.utils import timezone
from datetime import timedelta
import random
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Creates comprehensive production-ready mock data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before creating new data',
        )
    
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS('  CREATING PRODUCTION MOCK DATA'))
        self.stdout.write(self.style.SUCCESS('='*70 + '\n'))
        
        # Clear existing data if requested
        if kwargs.get('clear'):
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            try:
                GameResult.objects.all().delete()
                self.stdout.write(self.style.SUCCESS('✓ Deleted all game results'))
                
                Team.objects.all().delete()
                self.stdout.write(self.style.SUCCESS('✓ Deleted all teams'))
                
                Game.objects.all().delete()
                self.stdout.write(self.style.SUCCESS('✓ Deleted all games'))
                
                # Keep admin users, delete test users
                User.objects.filter(email__contains='@example.com').delete()
                self.stdout.write(self.style.SUCCESS('✓ Deleted test users\n'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error clearing data: {e}'))
        
        # =====================================================================
        # CREATE ADMIN USERS
        # =====================================================================
        self.stdout.write(self.style.WARNING('Creating Admin Users...'))
        admins = []
        
        admin_data = [
            {'email': 'admin@gameplatform.com', 'name': 'System Administrator'},
            {'email': 'manager@gameplatform.com', 'name': 'Platform Manager'},
        ]
        
        for data in admin_data:
            try:
                admin, created = User.objects.get_or_create(
                    email=data['email'],
                    defaults={
                        'name': data['name'],
                        'role': 'admin',
                        'is_staff': True,
                        'is_superuser': True,
                        'is_active': True,
                    }
                )
                if created:
                    admin.set_password('Admin@2024!')
                    admin.save()
                    self.stdout.write(self.style.SUCCESS(
                        f'✓ Created admin: {admin.email} (QR: {admin.qr_id})'
                    ))
                else:
                    self.stdout.write(f'  ⚠ Admin exists: {admin.email}')
                admins.append(admin)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating admin: {e}'))
        
        # =====================================================================
        # CREATE REGULAR USERS
        # =====================================================================
        self.stdout.write('\n' + self.style.WARNING('Creating Regular Users...'))
        users = []
        
        user_names = [
            'Alex Johnson', 'Maria Garcia', 'James Smith', 'Sarah Williams',
            'Michael Brown', 'Emma Davis', 'David Miller', 'Lisa Anderson',
            'Chris Taylor', 'Jessica Martinez', 'Daniel Thomas', 'Ashley Jackson',
            'Matthew White', 'Amanda Harris', 'Joshua Martin', 'Jennifer Thompson',
            'Andrew Garcia', 'Emily Robinson', 'Ryan Clark', 'Michelle Rodriguez'
        ]
        
        for i, name in enumerate(user_names, 1):
            email = name.lower().replace(' ', '.') + '@players.com'
            try:
                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={
                        'name': name,
                        'role': 'user',
                        'is_active': True,
                    }
                )
                if created:
                    user.set_password('Player@2024!')
                    user.save()
                    if i <= 5:  # Only show first 5 to avoid clutter
                        self.stdout.write(self.style.SUCCESS(
                            f'✓ Created user: {user.email} (QR: {user.qr_id})'
                        ))
                users.append(user)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating user {name}: {e}'))
        
        if len(users) > 5:
            self.stdout.write(f'  ... and {len(users) - 5} more users')
        
        # =====================================================================
        # CREATE GAMES
        # =====================================================================
        self.stdout.write('\n' + self.style.WARNING('Creating Games...'))
        games_data = [
            {
                'name': 'Basketball 3v3',
                'description': 'Street basketball tournament - 3 on 3 competition',
                'max_points': 21,
                'min_points': 0
            },
            {
                'name': 'Soccer League',
                'description': 'Weekly soccer matches - full team competition',
                'max_points': 10,
                'min_points': 0
            },
            {
                'name': 'Chess Tournament',
                'description': 'Strategic chess competition - individual matches',
                'max_points': 1,
                'min_points': 0
            },
            {
                'name': 'Tennis Doubles',
                'description': 'Doubles tennis matches on outdoor courts',
                'max_points': 6,
                'min_points': 0
            },
            {
                'name': 'Volleyball Beach',
                'description': 'Beach volleyball 4v4 competition',
                'max_points': 25,
                'min_points': 0
            },
            {
                'name': 'Table Tennis',
                'description': 'Fast-paced ping pong singles tournament',
                'max_points': 11,
                'min_points': 0
            },
            {
                'name': 'Badminton',
                'description': 'Indoor badminton singles and doubles',
                'max_points': 21,
                'min_points': 0
            },
            {
                'name': 'Running Sprint',
                'description': '100m and 200m sprint competitions',
                'max_points': 100,
                'min_points': 0
            },
            {
                'name': 'Swimming Relay',
                'description': 'Team swimming relay races',
                'max_points': 100,
                'min_points': 0
            },
            {
                'name': 'E-Sports FIFA',
                'description': 'FIFA video game tournament',
                'max_points': 5,
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
                    self.stdout.write(f'  ⚠ Game exists: {game.game_name}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating game {game_data["name"]}: {e}'))
        
        # =====================================================================
        # CREATE TEAMS
        # =====================================================================
        self.stdout.write('\n' + self.style.WARNING('Creating Teams...'))
        teams = []
        
        team_prefixes = ['Thunderbolts', 'Phoenix', 'Dragons', 'Warriors', 'Titans', 
                        'Lightning', 'Storm', 'Hurricanes', 'Vipers', 'Eagles',
                        'Panthers', 'Wolves', 'Sharks', 'Lions', 'Tigers']
        team_suffixes = ['United', 'Elite', 'Pro', 'Academy', 'Champions']
        
        teams_created = 0
        for user in users[:15]:  # Create teams for first 15 users
            num_teams = random.randint(2, 4)
            for _ in range(num_teams):
                team_name = f"{random.choice(team_prefixes)} {random.choice(team_suffixes)}"
                try:
                    team, created = Team.objects.get_or_create(
                        team_name=team_name,
                        user=user,
                        defaults={'is_active': True}
                    )
                    teams.append(team)
                    if created:
                        teams_created += 1
                        if teams_created <= 5:
                            self.stdout.write(self.style.SUCCESS(
                                f'✓ Created team: {team.team_name} (ID: {team.team_id}, Owner: {user.name})'
                            ))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f'Error creating team {team_name}: {e}'
                    ))
        
        if teams_created > 5:
            self.stdout.write(f'  ... and {teams_created - 5} more teams')
        
        # =====================================================================
        # CREATE GAME RESULTS
        # =====================================================================
        self.stdout.write('\n' + self.style.WARNING('Creating Game Results...'))
        results_created = 0
        
        # Create results for the last 30 days
        for team in teams:
            # Each team plays 3-8 games
            num_games = random.randint(3, 8)
            selected_games = random.sample(games, k=min(num_games, len(games)))
            
            for game in selected_games:
                try:
                    # Generate realistic score
                    points = random.randint(
                        int(game.min_points), 
                        int(game.max_points * 0.9)  # Usually not max score
                    )
                    
                    # Random date in last 30 days
                    days_ago = random.randint(0, 30)
                    played_date = timezone.now() - timedelta(days=days_ago)
                    
                    # 30% chance to be verified by admin
                    verified = random.random() < 0.3
                    admin_verifier = random.choice(admins) if verified else None
                    
                    result = GameResult.objects.create(
                        user=team.user,
                        team=team,
                        game=game,
                        points_scored=points,
                        notes=f'Match played on {played_date.strftime("%Y-%m-%d")}',
                        verified_by_admin=verified,
                        admin_user=admin_verifier,
                    )
                    
                    # Update played_at to simulated date
                    GameResult.objects.filter(result_id=result.result_id).update(
                        played_at=played_date
                    )
                    
                    results_created += 1
                    if results_created <= 5:
                        status = '✓ Verified' if verified else '○ Unverified'
                        self.stdout.write(self.style.SUCCESS(
                            f'{status} Result: {team.team_name} - {game.game_name}: {points} pts'
                        ))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f'Error creating result for {team.team_name}: {e}'
                    ))
        
        if results_created > 5:
            self.stdout.write(f'  ... and {results_created - 5} more results')
        
        # =====================================================================
        # SUMMARY
        # =====================================================================
        self.stdout.write('\n' + self.style.SUCCESS('='*70))
        self.stdout.write(self.style.SUCCESS('  PRODUCTION DATA CREATED SUCCESSFULLY'))
        self.stdout.write(self.style.SUCCESS('='*70))
        
        self.stdout.write(f'\n{self.style.WARNING("DATABASE SUMMARY:")}')
        self.stdout.write(f'  Total Users: {User.objects.count()}')
        
        # Count admins and players (filter in Python to avoid djongo boolean issues)
        all_users = list(User.objects.all())
        admin_count = len([u for u in all_users if u.role == "admin"])
        player_count = len([u for u in all_users if u.role == "user"])
        
        self.stdout.write(f'    - Admins: {admin_count}')
        self.stdout.write(f'    - Players: {player_count}')
        self.stdout.write(f'  Total Games: {Game.objects.count()}')
        self.stdout.write(f'  Total Teams: {Team.objects.count()}')
        self.stdout.write(f'  Total Results: {GameResult.objects.count()}')
        
        # Count verified results (filter in Python to avoid djongo boolean issues)
        all_results = list(GameResult.objects.all())
        verified_count = len([r for r in all_results if r.verified_by_admin])
        pending_count = len([r for r in all_results if not r.verified_by_admin])
        
        self.stdout.write(f'    - Verified: {verified_count}')
        self.stdout.write(f'    - Pending: {pending_count}')
        
        self.stdout.write(f'\n{self.style.WARNING("CREDENTIALS:")}')
        self.stdout.write('  Admin Accounts:')
        self.stdout.write('    admin@gameplatform.com / Admin@2024!')
        self.stdout.write('    manager@gameplatform.com / Admin@2024!')
        self.stdout.write('\n  Player Accounts (all use: Player@2024!):')
        self.stdout.write('    alex.johnson@players.com')
        self.stdout.write('    maria.garcia@players.com')
        self.stdout.write('    ... (and 18 more)')
        
        self.stdout.write('\n' + self.style.SUCCESS('='*70))
        self.stdout.write(self.style.SUCCESS('  Ready for production testing!'))
        self.stdout.write(self.style.SUCCESS('='*70 + '\n'))
