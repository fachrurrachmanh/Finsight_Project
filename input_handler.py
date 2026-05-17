class InputHandler:
    def input_manual(self):
        print("\n=== INPUT DATA PERUSAHAAN ===")

        #profil perusahaan
        #=========================
        nama = input("Nama perusahaan: ")
        ticker = input("Kode saham: ")
        sektor = input("Sektor: ")
        harga = float(input("Harga pasar saat ini: ") or 0)

        #jumlah tahun
        # =========================
        jumlah_tahun = int(input("Berapa tahun data? ") or 3)
        tahun_akhir = int(input("Tahun terakhir: ") or 2023)

        tahun_list = list(range(
            tahun_akhir - jumlah_tahun + 1,
            tahun_akhir + 1
        ))

        neraca_list = []
        laba_rugi_list = []
        arus_kas_list = []


        # input per tahun
        # =========================
        for tahun in tahun_list:
            print(f"\n===== TAHUN {tahun} =====")

            #neraca
            # ========
            print("\n--- Neraca ---")

            kas = float(input("Kas: ") or 0)
            piutang = float(input("Piutang: ") or 0)
            persediaan = float(input("Persediaan: ") or 0)

            total_aset = float(input("Total aset: ") or 0)
            total_liabilitas = float(input("Total liabilitas: ") or 0)
            total_ekuitas = float(input("Total ekuitas: ") or 0)

            neraca = {
                "tahun": tahun,
                "kas": kas,
                "piutang": piutang,
                "persediaan": persediaan,
                "total_aset": total_aset,
                "total_liabilitas": total_liabilitas,
                "total_ekuitas": total_ekuitas
            }

            neraca_list.append(neraca)

            #laba rugi
            #==============
            print("\n--- Laba Rugi ---")

            pendapatan = float(input("Pendapatan: ") or 0)
            hpp = float(input("HPP: ") or 0)
            laba_bersih = float(input("Laba bersih: ") or 0)

            laba_rugi = {
                "tahun": tahun,
                "pendapatan": pendapatan,
                "hpp": hpp,
                "laba_bersih": laba_bersih
            }

            laba_rugi_list.append(laba_rugi)

            #arus kas
            #==========
            print("\n--- Arus Kas ---")

            cfo = float(input("Cash Flow Operasi: ") or 0)
            capex = float(input("Capex: ") or 0)
            free_cash_flow = cfo - capex

            arus_kas = {
                "tahun": tahun,
                "cfo": cfo,
                "capex": capex,
                "fcf": free_cash_flow
            }

            arus_kas_list.append(arus_kas)

            print(f"\nData tahun {tahun} berhasil disimpan.")

        # hasil akhir
        # =========================
        data = {
            "profil": {
                "nama": nama,
                "ticker": ticker,
                "sektor": sektor,
                "harga": harga
            },
            "neraca": neraca_list,
            "laba_rugi": laba_rugi_list,
            "arus_kas": arus_kas_list
        }

        return data

