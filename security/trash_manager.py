import os
import shutil
from datetime import datetime


class TrashManager:
    def __init__(self, trash_folder="deleted_things"):
        self.trash_folder = trash_folder
        # Əgər qovluq yoxdursa, yaradırıq
        if not os.path.exists(self.trash_folder):
            os.makedirs(self.trash_folder)

    def safe_delete(self, file_path):
        """Faylı silmir, 'deleted_things' qovluğuna daşıyır."""
        try:
            if not os.path.exists(file_path):
                print(f" Səhv: '{file_path}' faylı tapılmadı.")
                return

            # Eyni adlı fayllar qarışmasın deyə adın sonuna vaxt əlavə edirik
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.basename(file_path)
            new_name = f"deleted_{timestamp}_{filename}"

            destination = os.path.join(self.trash_folder, new_name)

            # Faylı daşıyırıq (move)
            shutil.move(file_path, destination)
            print(f" Fayl 'trash'-ə göndərildi: {destination}")

        except Exception as e:
            print(f" Silinmə zamanı xəta baş verdi: {e}")