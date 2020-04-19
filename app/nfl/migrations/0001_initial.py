# Generated by Django 3.0.5 on 2020-04-01 16:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField()),
                ('home_team_score', models.PositiveSmallIntegerField(default=None, null=True)),
                ('visitor_team_score', models.PositiveSmallIntegerField(default=None, null=True)),
                ('final', models.BooleanField(default=False)),
            ],
            options={'get_latest_by': 'week'},
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.CharField(choices=[('ATL', 'Atlanta'), ('BAL', 'Baltimore'), ('CHA', 'Charlotte'), ('CHI', 'Chicago'), ('CIN', 'Cincinnati'), ('CLE', 'Cleveland'), ('DEN', 'Denver'), ('DET', 'Detroit'), ('ER', 'East Rutherford'), ('FOX', 'Foxborough'), ('GLE', 'Glendale'), ('GB', 'Green Bay'), ('HOU', 'Houston'), ('IND', 'Indianapolis'), ('IRV', 'Irving'), ('JAX', 'Jacksonville'), ('KC', 'Kansas City'), ('LA', 'Los Angeles'), ('LAN', 'Landover'), ('MIA', 'Miami'), ('MIN', 'Minneapolis'), ('NAS', 'Nashville'), ('NO', 'New Orleans'), ('OAK', 'Oakland'), ('OP', 'Orchard Park'), ('ORL', 'Orlando'), ('PHI', 'Philadelphia'), ('PIT', 'Pittsburgh'), ('SF', 'San Francisco'), ('SEA', 'Seattle'), ('TAM', 'Tampa')], default='ATL', max_length=3)),
                ('abbr', models.CharField(choices=[('AFC', 'American Football Conference'), ('CHI', 'Chicago Bears'), ('CIN', 'Cincinnati Bengals'), ('BUF', 'Buffalo Bills'), ('DEN', 'Denver Broncos'), ('CLE', 'Cleveland Browns'), ('TB', 'Tampa Bay Buccaneers'), ('ARI', 'Arizona Cardinals'), ('LAC', 'Los Angeles Chargers'), ('KC', 'Kansas City Chiefs'), ('IND', 'Indianapolis Colts'), ('DAL', 'Dallas Cowboys'), ('MIA', 'Miami Dolphins'), ('PHI', 'Philadelphia Eagles'), ('ATL', 'Atlanta Falcons'), ('SF', 'San Francisco 49ers'), ('NYG', 'New York Giants'), ('JAX', 'Jacksonville Jaguars'), ('NYJ', 'New York Jets'), ('DET', 'Detroit Lions'), ('NFC', 'National Football Conference'), ('GB', 'Green Bay Packers'), ('CAR', 'Carolina Panthers'), ('NE', 'New England Patriots'), ('OAK', 'Oakland Raiders'), ('LA', 'Los Angeles Rams'), ('BAL', 'Baltimore Ravens'), ('WAS', 'Washington Redskins'), ('NO', 'New Orleans Saints'), ('SEA', 'Seattle Seahawks'), ('PIT', 'Pittsburgh Steelers'), ('HOU', 'Houston Texans'), ('TEN', 'Tennessee Titans'), ('MIN', 'Minnesota Vikings')], default='ARI', max_length=3)),
                ('stadium', models.CharField(choices=[('AS', 'Arrowhead Stadium'), ('ATS', 'AT&T Stadium'), ('BAS', 'Bank of America Stadium'), ('CLF', 'CenturyLink Field'), ('CWS', 'Camping World Stadium'), ('DHSP', 'Dignity Health Sports Park'), ('EF', 'Empower Field at Mile High'), ('FEF', 'FedExField'), ('FES', 'FirstEnergy Stadium'), ('FF', 'Ford Field'), ('GS', 'Gillette Stadium'), ('HF', 'Heinz Field'), ('HRS', 'Hard Rock Stadium'), ('LAMC', 'Los Angeles Memorial Coliseum'), ('LF', 'Lambeau Field'), ('LFF', 'Lincoln Financial Field'), ('LS', "Levi's Stadium"), ('LOS', 'Lucas Oil Stadium'), ('MBS', 'Mercedes-Benz Stadium'), ('MBD', 'Mercedes-Benz Superdome'), ('MLS', 'MetLife Stadium'), ('MTBS', 'M&T Bank Stadium'), ('NEF', 'New Era Field'), ('NRGS', 'NRG Stadium'), ('NS', 'Nissan Stadium'), ('PBS', 'Paul Brown Stadium'), ('RCC', 'RingCentral Coliseum'), ('RJS', 'Raymond James Stadium'), ('SF', 'Soldier Field'), ('SFS', 'State Farm Stadium'), ('TBF', 'TIAA Bank Field'), ('USBS', 'U.S. Bank Stadium')], default='AS', max_length=4)),
            ],
        ),
        migrations.CreateModel(
            name='Year',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.PositiveSmallIntegerField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Week',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('week', models.PositiveSmallIntegerField()),
                ('year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nfl.Year')),
            ],
            options={
                'unique_together': {('year', 'week')},
            },
        ),
        migrations.CreateModel(
            name='Pick',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('selection', models.SmallIntegerField(choices=[(0, 'Tbp'), (1, 'Home Team'), (2, 'Visitor Team'), (3, 'Tied Game')], default=0)),
                ('picked_tie_break', models.PositiveSmallIntegerField(default=0)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='picks', to='nfl.Game')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='picks', to=settings.AUTH_USER_MODEL)),
            ],
            options={'get_latest_by': 'game__week'},
        ),
        migrations.AddField(
            model_name='game',
            name='home_team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='home_teams', to='nfl.Team'),
        ),
        migrations.AddField(
            model_name='game',
            name='visitor_team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='visitor_teams', to='nfl.Team'),
        ),
        migrations.AddField(
            model_name='game',
            name='week',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='games', to='nfl.Week'),
        ),
    ]

