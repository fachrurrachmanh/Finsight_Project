# ══════════════════════════════════════════════════════
# FUNGSI INTERNAL — PENGGABUNGAN DUA SUB-LIST
# ══════════════════════════════════════════════════════

def _gabung(kiri, kanan, key, reverse):
    """
    Gabungkan dua sub-list yang sudah terurut menjadi satu list terurut.

    Tahap "merge" dari Merge Sort:
        - Bandingkan elemen terdepan kiri vs kanan
        - Ambil yang lebih kecil (ascending) atau lebih besar (descending)
        - Ulangi sampai salah satu sub-list habis
        - Tempelkan sisa sub-list yang belum habis
    """
    hasil = []
    i = 0  # indeks penjelajah sub-list kiri
    j = 0  # indeks penjelajah sub-list kanan

    while i < len(kiri) and j < len(kanan):
        # Ekstrak nilai kunci untuk perbandingan
        val_kiri  = key(kiri[i])  if key is not None else kiri[i]
        val_kanan = key(kanan[j]) if key is not None else kanan[j]

        # Tentukan sub-list mana yang memberikan elemen berikutnya
        if reverse:
            # Descending: ambil yang LEBIH BESAR duluan
            # Jika nilai kiri >= kanan → kiri masuk lebih dulu
            ambil_kiri = (val_kiri >= val_kanan)
        else:
            # Ascending: ambil yang LEBIH KECIL duluan
            # Jika nilai kiri <= kanan → kiri masuk lebih dulu
            ambil_kiri = (val_kiri <= val_kanan)

        if ambil_kiri:
            hasil.append(kiri[i])
            i += 1
        else:
            hasil.append(kanan[j])
            j += 1

    # Tempelkan sisa elemen yang belum diproses
    # (hanya satu dari dua cabang di bawah yang akan berjalan)
    while i < len(kiri):
        hasil.append(kiri[i])
        i += 1
    while j < len(kanan):
        hasil.append(kanan[j])
        j += 1

    return hasil


# ══════════════════════════════════════════════════════
# FUNGSI UTAMA — MERGE SORT
# ══════════════════════════════════════════════════════

def merge_sort(arr, key=None, reverse=False):
    """
    Urutkan iterable menggunakan algoritma Merge Sort rekursif.

    Parameters
    ----------
    arr     : list / iterable
        Koleksi elemen yang akan diurutkan.
    key     : callable | None
        Fungsi satu argumen untuk mengekstrak nilai kunci perbandingan.
        Contoh: key=lambda x: x.tahun
                key=lambda x: x[1]
                key=lambda x: x.stat().st_mtime
        Jika None, elemen dibandingkan langsung.
    reverse : bool
        False (default) → urutan menaik (ascending, terkecil pertama)
        True            → urutan menurun (descending, terbesar pertama)

    Returns
    -------
    list
        List baru yang sudah terurut. List asli tidak dimodifikasi.
    """
    # Konversi ke list agar bisa di-slice (mendukung generator, set, dll.)
    arr = list(arr)

    # Base case: list dengan 0 atau 1 elemen sudah terurut
    if len(arr) <= 1:
        return arr

    # Divide: belah tepat di tengah
    titik_tengah = len(arr) // 2
    sub_kiri     = arr[:titik_tengah]
    sub_kanan    = arr[titik_tengah:]

    # Conquer: rekursi pada masing-masing paruh
    kiri_terurut  = merge_sort(sub_kiri,  key=key, reverse=reverse)
    kanan_terurut = merge_sort(sub_kanan, key=key, reverse=reverse)

    # Combine: gabungkan dua paruh terurut
    return _gabung(kiri_terurut, kanan_terurut, key=key, reverse=reverse)
