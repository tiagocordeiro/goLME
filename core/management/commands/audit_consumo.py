import csv
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db.models import Count, Max
from django.utils import timezone

from core.models import ApiRequestLog, Profile


class Command(BaseCommand):
    help = "Audita o consumo da API por conta numa janela de dias (default 30)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dias", type=int, default=30,
            help="Tamanho da janela de análise, em dias. Default: 30.",
        )
        parser.add_argument(
            "--csv", dest="csv_path", default=None,
            help="Se informado, exporta o consumo por conta para este caminho .csv.",
        )

    def handle(self, *args, **opts):
        dias = opts["dias"]
        desde = timezone.now() - timedelta(days=dias)
        logs = ApiRequestLog.objects.filter(timestamp__gte=desde)

        total = logs.count()
        self.stdout.write(self.style.MIGRATE_HEADING(
            f"\n=== Auditoria de consumo goLME — últimos {dias} dias ==="
        ))
        self.stdout.write(f"Total de requisições registradas: {total}\n")

        # 1) Consumo por conta identificada (key bate com um Profile)
        por_conta = list(
            logs.filter(profile__isnull=False)
            .values(
                "profile__user__username",
                "profile__user__email",
                "profile__api_secret_key",
                "profile__site_url",
            )
            .annotate(
                requests=Count("id"),
                ultimo=Max("timestamp"),
                ips=Count("ip", distinct=True),
            )
            .order_by("-requests")
        )

        self.stdout.write(self.style.HTTP_INFO("→ Contas ATIVAS (consumindo no período):"))
        if not por_conta:
            self.stdout.write("  (nenhuma)")
        for row in por_conta:
            # Tratamento de limites para não quebrar a tela
            username = str(row['profile__user__username'] or '-')[:22]
            email = str(row['profile__user__email'] or '-')[:30]
            site = str(row['profile__site_url'] or '-')[:40]

            self.stdout.write(
                f"  {username:<24} "
                f"{email:<32} "
                f"reqs={row['requests']:<7} ips={row['ips']:<4} "
                f"último={row['ultimo']:%Y-%m-%d %H:%M} "
                f"site={site}"
            )

        # 2) Contas com key que NÃO consumiram no período (dormentes)
        ativos_keys = {r["profile__api_secret_key"] for r in por_conta}
        dormentes = (
            Profile.objects.exclude(api_secret_key__isnull=True)
            .exclude(api_secret_key="")
            .exclude(api_secret_key__in=ativos_keys)
            .select_related("user")
            .order_by("user__username")
        )
        self.stdout.write(self.style.HTTP_INFO("\n→ Contas DORMENTES (têm key, sem consumo no período):"))
        if not dormentes:
            self.stdout.write("  (nenhuma)")
        for p in dormentes:
            # Tratamento de limites para contas dormentes
            username = str(p.user.username or '-')[:22]
            email = str(p.user.email or '-')[:30]
            site = str(p.site_url or '-')[:40]

            self.stdout.write(f"  {username:<24} {email:<32} site={site}")

        # 3) Keys INVÁLIDAS apresentadas (não batem com nenhum Profile) — possível abuso
        invalidas = list(
            logs.filter(profile__isnull=True)
            .exclude(api_key_used="")
            .values("api_key_used")
            .annotate(requests=Count("id"), ultimo=Max("timestamp"), ips=Count("ip", distinct=True))
            .order_by("-requests")
        )
        self.stdout.write(self.style.HTTP_INFO("\n→ Keys INVÁLIDAS apresentadas (não existem no sistema):"))
        if not invalidas:
            self.stdout.write("  (nenhuma)")
        for row in invalidas:
            # Tratamento de limite para a chave (pode vir algum lixo gigantesco no request)
            key_invalida = str(row['api_key_used'] or '-')[:38]

            self.stdout.write(
                f"  {key_invalida:<40} reqs={row['requests']:<7} "
                f"ips={row['ips']:<4} último={row['ultimo']:%Y-%m-%d %H:%M}"
            )

        # 4) Acesso anônimo (rota de API sem key, ex.: /summary/)
        anon = logs.filter(profile__isnull=True, api_key_used="").count()
        self.stdout.write(self.style.HTTP_INFO("\n→ Requisições anônimas (rota de API sem key):"))
        self.stdout.write(f"  {anon}")

        # Export opcional
        if opts["csv_path"]:
            with open(opts["csv_path"], "w", newline="", encoding="utf-8") as fh:
                w = csv.writer(fh)
                w.writerow(["username", "email", "api_secret_key", "site_url", "requests", "ips", "ultimo"])
                for row in por_conta:
                    w.writerow([
                        row["profile__user__username"],
                        row["profile__user__email"],
                        row["profile__api_secret_key"],
                        row["profile__site_url"],
                        row["requests"],
                        row["ips"],
                        row["ultimo"].strftime("%Y-%m-%d %H:%M:%S"),
                    ])
            self.stdout.write(self.style.SUCCESS(f"\nCSV exportado em: {opts['csv_path']}"))

        self.stdout.write("")