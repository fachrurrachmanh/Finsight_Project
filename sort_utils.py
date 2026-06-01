"""
sort_utils.py — Algoritma Pengurutan Kustom (Merge Sort)
=========================================================
Menggantikan fungsi built-in sorted() di seluruh modul FinSight.

Algoritma  : Merge Sort
Kompleksitas:
    Waktu   — O(n log n) untuk semua kasus (terbaik / rata-rata / terburuk)
    Ruang   — O(n) ruang tambahan untuk array bantu saat proses penggabungan

Kelebihan Merge Sort vs alternatif lain:
    ✔  Stabil: elemen dengan nilai kunci sama mempertahankan urutan aslinya
    ✔  Deterministik: tidak bergantung pada kondisi awal data (berbeda Quick Sort)
    ✔  Konsisten: tidak ada kasus terburuk O(n²) seperti Bubble/Insertion/Quick Sort
    ✔  Cocok untuk key-based sort (objek, tuple, Path) yang digunakan di proyek ini

Cara pakai (pengganti sorted()):
    merge_sort(arr)                              → ascending tanpa key
    merge_sort(arr, key=lambda x: x.tahun)       → ascending berdasarkan .tahun
    merge_sort(arr, key=lambda x: x[1], reverse=True)  → descending berdasarkan indeks 1
"""


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

    Contoh
    ------
    >>> merge_sort([3, 1, 4, 1, 5])
    [1, 1, 3, 4, 5]

    >>> merge_sort([3, 1, 4], reverse=True)
    [4, 3, 1]

    >>> data = [('b', 2), ('a', 5), ('c', 1)]
    >>> merge_sort(data, key=lambda x: x[1])
    [('c', 1), ('b', 2), ('a', 5)]

    Cara kerja rekursif
    -------------------
    merge_sort([8, 3, 5, 1])
        ├─ merge_sort([8, 3])
        │    ├─ merge_sort([8]) → [8]      ← base case
        │    ├─ merge_sort([3]) → [3]      ← base case
        │    └─ _gabung([8],[3]) → [3, 8]
        ├─ merge_sort([5, 1])
        │    ├─ merge_sort([5]) → [5]      ← base case
        │    ├─ merge_sort([1]) → [1]      ← base case
        │    └─ _gabung([5],[1]) → [1, 5]
        └─ _gabung([3,8],[1,5]) → [1, 3, 5, 8]
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
