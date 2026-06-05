import csv
from django.core.management.base import BaseCommand
from restaurants.models import Restaurant


class Command(BaseCommand):
    help = 'CSV 파일에서 식당 데이터를 DB에 import합니다'

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str, help='CSV 파일 경로')

    def handle(self, *args, **options):
        csv_path = options['csv_path']
        created_count = 0
        updated_count = 0
        skipped_count = 0

        with open(csv_path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name     = row.get('restaurant_name', '').strip()
                naver_id = row.get('id', '').strip()
                picture  = row.get('picture', '').strip()

                if not naver_id or not name or not picture:
                    self.stdout.write(self.style.WARNING(
                        f'스킵 (데이터 누락): name={name!r}, naver_id={naver_id!r}'
                    ))
                    skipped_count += 1
                    continue

                _, created = Restaurant.objects.update_or_create(
                    naver_id=naver_id,
                    defaults={'name': name, 'picture': picture},
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'완료: {created_count}개 추가 / {updated_count}개 업데이트 / {skipped_count}개 스킵'
        ))