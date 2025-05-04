"""
python manage.py import_cotacoes LondonMetalExchange-2025-05-02.csv
"""
import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
import os

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import LondonMetalExchange


class Command(BaseCommand):
    help = 'Importa cotações do London Metal Exchange a partir de um arquivo CSV'

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str, help='Caminho para o arquivo CSV com as cotações')

    def handle(self, *args, **options):
        csv_path = options['csv_path']

        # Verificar se o arquivo existe
        if not os.path.exists(csv_path):
            raise CommandError(f'O arquivo {csv_path} não existe')

        # Verificar se o arquivo é um CSV
        if not csv_path.endswith('.csv'):
            raise CommandError(f'O arquivo {csv_path} não é um arquivo CSV')

        self.stdout.write(self.style.SUCCESS(f'Iniciando importação do arquivo {csv_path}'))

        # Contador para estatísticas
        records_created = 0
        records_updated = 0
        records_with_errors = 0

        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                # Detectar o delimitador (vírgula ou ponto-e-vírgula são comuns)
                sample = file.read(1024)
                file.seek(0)

                dialect = csv.Sniffer().sniff(sample, delimiters=',;')
                reader = csv.DictReader(file, dialect=dialect)

                # Confirmar que as colunas correspondem ao modelo
                expected_fields = ['date', 'cobre', 'zinco', 'aluminio', 'chumbo', 'estanho', 'niquel', 'dolar']
                if not all(field in reader.fieldnames for field in expected_fields):
                    missing_fields = [field for field in expected_fields if field not in reader.fieldnames]
                    raise CommandError(f'O CSV não contém todas as colunas necessárias. Faltando: {", ".join(missing_fields)}')

                # Usar uma transação para garantir a integridade dos dados
                with transaction.atomic():
                    for row in reader:
                        try:
                            # Converter a data para o formato do Django
                            try:
                                date_value = datetime.strptime(row['date'], '%Y-%m-%d').date()
                            except ValueError:
                                # Tentar formato alternativo se o primeiro falhar
                                try:
                                    date_value = datetime.strptime(row['date'], '%d/%m/%Y').date()
                                except ValueError:
                                    self.stdout.write(self.style.WARNING(f'Formato de data inválido: {row["date"]}'))
                                    records_with_errors += 1
                                    continue

                            # Converter valores para Decimal, limpando formatação se necessário
                            decimal_fields = {}
                            for field in expected_fields[1:]:  # Todos exceto 'date'
                                try:
                                    # Limpar formatação (substituir vírgula por ponto e remover espaços)
                                    clean_value = row[field].replace('.', '').replace(',', '.').strip()
                                    decimal_fields[field] = Decimal(clean_value)
                                except (InvalidOperation, AttributeError) as e:
                                    self.stdout.write(self.style.WARNING(
                                        f'Erro ao converter valor para {field}: {row[field]} - {str(e)}'
                                    ))
                                    records_with_errors += 1
                                    continue

                            # Tentar atualizar ou criar o registro
                            obj, created = LondonMetalExchange.objects.update_or_create(
                                date=date_value,
                                defaults={
                                    'cobre': decimal_fields['cobre'],
                                    'zinco': decimal_fields['zinco'],
                                    'aluminio': decimal_fields['aluminio'],
                                    'chumbo': decimal_fields['chumbo'],
                                    'estanho': decimal_fields['estanho'],
                                    'niquel': decimal_fields['niquel'],
                                    'dolar': decimal_fields['dolar'],
                                }
                            )

                            if created:
                                records_created += 1
                            else:
                                records_updated += 1

                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f'Erro ao processar linha: {row} - {str(e)}'))
                            records_with_errors += 1

        except Exception as e:
            raise CommandError(f'Erro ao processar o arquivo CSV: {str(e)}')

        # Exibir estatísticas de importação
        self.stdout.write(self.style.SUCCESS(f'Importação concluída:'))
        self.stdout.write(f'  - Registros criados: {records_created}')
        self.stdout.write(f'  - Registros atualizados: {records_updated}')
        self.stdout.write(f'  - Registros com erros: {records_with_errors}')
