from rich.console import Console
from rich.prompt import Prompt

console = Console()


def validasi_data(data):

    field_dibutuhkan = [

        "perusahaan",
        "harga",
        "eps",
        "book_value",
        "laba_bersih",
        "total_aset",
        "total_utang",
        "aset_lancar",
        "utang_lancar"
    ]

    for field in field_dibutuhkan:

        if field not in data:

            console.print(
                f"[red]Missing field:[/red] {field}"
            )

            return False

    return True


def manual_input():

    console.print(
        "\n[bold cyan]Input Keunagan[/bold cyan]\n"
    )

    try:

        data = {

            "perusahaan":
                Prompt.ask("ticker perusahaan"),

            "harga":
                float(
                    Prompt.ask("harga saham")
                ),

            "eps":
                float(
                    Prompt.ask("EPS")
                ),

            "book_value":
                float(
                    Prompt.ask(
                        "Book Value per saham"
                    )
                ),

            "laba_bersih":
                float(
                    Prompt.ask("laba bersih")
                ),

            "total_aset":
                float(
                    Prompt.ask("total aset")
                ),

            "total_utang":
                float(
                    Prompt.ask("total utang")
                ),

            "aset_lancar":
                float(
                    Prompt.ask(
                        "aset lancar"
                    )
                ),

            "utang_lancar":
                float(
                    Prompt.ask(
                        "utang/kewajiban lancar"
                    )
                )
        }

        #validasi
        if validasi_data(data):

            console.print(
                "\n[green]input berhasil[/green]"
            )

            return data

        return None

    except ValueError:

        console.print(
            "[red]input harus berupa angka[/red]"
        )

        return None
    
if __name__ == "__main__":

    data = manual_input()

    print(data)

