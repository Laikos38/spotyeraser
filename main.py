from gui.main_gui import *
from gui import resources_rc
from utils import spotipy_handler
from queue import Queue
from functools import partial
from sys import exit as exit_app

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        # Load window design
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)

        # Attr
        self.items_to_erase = []

        # Hide elements
        self.progress_pb.setVisible(False)

        # Spotipy
        self.spotipy_handler = spotipy_handler.SpotipyHandler()
        
        # Thread
        self.thread = QtCore.QThread()
        self.worker = self.spotipy_handler
        self.worker.moveToThread(self.thread)
        self.worker.started.connect(lambda: self.progress_pb.setVisible(True))
        self.worker.started.connect(lambda: self.erase_gb.setEnabled(False))
        self.worker.finished.connect(lambda: self.progress_pb.setVisible(False))
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.thread.quit)

        # Buttons
        self.connect_btn.clicked.connect(self.connect)
        self.validate_btn.clicked.connect(self.validate)
        self.erase_btn.clicked.connect(self.erase)
        self.select_all_btn.clicked.connect(lambda: self.select_all(True))
        self.unselect_all_btn.clicked.connect(lambda: self.select_all(False))

        # Combobox
        self.select_type_cmb.currentIndexChanged.connect(self.get_items)

        # Warning box
        self.msg_box = QtWidgets.QMessageBox

        # MenuBar
        self.actionExit.triggered.connect(lambda: exit_app())
        self.actionAbout.triggered.connect(self.open_about)

    def clear_thread_connections(self):
        self.thread.started.disconnect()
        self.worker.progress.disconnect()
        self.worker.finished.disconnect()
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(lambda: self.progress_pb.setVisible(False))
        self.worker.finished.connect(lambda: self.erase_gb.setEnabled(True))
        self.worker.started.connect(lambda: self.progress_pb.setVisible(True))

    def connect(self):
        self.spotipy_handler.login(False, False)
        self.status_sb.showMessage("Login...")
        self.login_link_txt.setEnabled(True)
        self.login_link_lbl.setEnabled(True)
        self.login_link_lbl.setEnabled(True)
        self.login_connect_lbl.setEnabled(True)
        self.login_validate_lbl.setEnabled(True)
        self.validate_btn.setEnabled(True)
    
    def validate(self):
        link = self.login_link_txt.toPlainText()
        if not link:
            self.login_error()
            return
            
        self.thread.started.connect(lambda: self.spotipy_handler.set_token_from_link(link))
        self.worker.finished.connect(self.get_user_data)
        self.thread.start()

    def get_user_data(self, result):
        if not result:
            self.login_error()
            return
        self.status_sb.showMessage("Login successful!")
        self.login_gb.setEnabled(False)
        self.erase_gb.setEnabled(True)
        # self.clear_thread_connections()
        # self.thread.started.connect(self.spotipy_handler.get_user_data)
        # self.worker.finished.connect(self.load_user_data)
        # self.thread.start()

    def load_user_data(self, user_data):
        pass
        # if user_data:
        #     self.user_gb.setTitle("User: " + str(user_data['username']))
        #     self.total_liked_tracks_lbl.setText("Total liked tracks: " + str(user_data['total_tracks']))
        #     self.total_followed_artists_lbl.setText("Total followed artists: " + str(user_data['total_artists']))
        #     self.total_liked_albums_lbl.setText("Total liked albums: " + str(user_data['total_albums']))
        #     self.total_liked_shows_lbl.setText("Total liked podcasts: " + str(user_data['total_shows']))
        #     self.user_gb.setVisible(True)
        # else:
        #     self.status_sb.showMessage("Error getting user info!")

    def login_error(self):
        self.status_sb.showMessage("The pasted link is not valid!")
        self.login_link_lbl.setEnabled(False)
        self.login_connect_lbl.setEnabled(False)
        self.login_validate_lbl.setEnabled(False)
        self.validate_btn.setEnabled(False)

    def get_items(self):
        self.list_l.clear()
        idx = self.select_type_cmb.currentIndex()
        self.clear_thread_connections()
        if idx == 0:
            self.thread.started.connect(self.spotipy_handler.current_user_saved_tracks)
            self.worker.progress.connect(self.update_progress)
            self.worker.finished.connect(self.load_tracks)
        elif idx == 1:
            self.thread.started.connect(self.spotipy_handler.current_user_saved_artists)
            self.worker.progress.connect(self.update_progress)
            self.worker.finished.connect(self.load_artists)
        elif idx == 2:
            self.thread.started.connect(self.spotipy_handler.current_user_saved_albums)
            self.worker.progress.connect(self.update_progress)
            self.worker.finished.connect(self.load_albums)
        elif idx == 3:
            self.thread.started.connect(self.spotipy_handler.current_user_saved_shows)
            self.worker.progress.connect(self.update_progress)
            self.worker.finished.connect(self.load_shows)
        self.thread.start()
    
    def load_tracks(self, all_tracks):
        if not all_tracks:
            self.status_sb.showMessage("You don't have any liked tracks in your library!")
            return
        for track in all_tracks:
            item = QtWidgets.QListWidgetItem(self.spotipy_handler.get_track_info_as_string(track))
            item.setData(32, track)
            self.list_l.addItem(item)

    def load_artists(self, all_artists):
        if not all_artists:
            self.status_sb.showMessage("You don't have any followed artists in your library!")
            return
        for artist in all_artists:
            item = QtWidgets.QListWidgetItem(self.spotipy_handler.get_artist_info_as_string(artist))
            item.setData(32, artist)
            self.list_l.addItem(item)

    def load_albums(self, all_albums):
        if not all_albums:
            self.status_sb.showMessage("You don't have any liked albums in your library!")
            return
        for album in all_albums:
            item = QtWidgets.QListWidgetItem(self.spotipy_handler.get_album_info_as_string(album))
            item.setData(32, album)
            self.list_l.addItem(item)

    def load_shows(self, all_shows):
        if not all_shows:
            self.status_sb.showMessage("You don't have any liked podcasts in your library!")
            return
        for show in all_shows:
            item = QtWidgets.QListWidgetItem(self.spotipy_handler.get_show_info_as_string(show))
            item.setData(32, show)
            self.list_l.addItem(item)

    def erase(self):
        idx = self.select_type_cmb.currentIndex()
        if idx == 0:
            self.erase_tracks()
        elif idx == 1:
            self.erase_artists()
        elif idx == 2:
            self.erase_albums()
        elif idx == 3:
            self.erase_shows()

    def erase_tracks(self):
        if not self.warning("This action will delete all the selected liked songs. Are you sure you wanna continue?"):
            return
        selected_items = self.list_l.selectedItems()
        if not selected_items:
            self.status_sb.showMessage("Select at least one track first!")
            return
        selected_items[:] = [item.data(32) for item in selected_items]
        self.clear_thread_connections()
        self.thread.started.connect(partial(self.spotipy_handler.erase_user_saved_tracks, selected_items))
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.result_erase_tracks)
        self.thread.start()
    
    def result_erase_tracks(self, result):
        if result:
            self.status_sb.showMessage("Tracks erased successfully!")
            self.success("Tracks erased successfully!")
        else:
            self.status_sb.showMessage("An error occurred during the erase process :(")
            self.error("An error occurred during the erase process :(")
        self.get_items()

    def erase_artists(self):
        if not self.warning("This action will delete all the selected followed artists. Are you sure you wanna continue?"):
            return
        selected_items = self.list_l.selectedItems()
        if not selected_items:
            self.status_sb.showMessage("Select at least one artist first!")
            return
        selected_items[:] = [item.data(32) for item in selected_items]
        self.clear_thread_connections()
        self.thread.started.connect(partial(self.spotipy_handler.erase_user_saved_artists, selected_items))
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.result_erase_artists)
        self.thread.start()
    
    def result_erase_artists(self, result):
        if result:
            self.status_sb.showMessage("Artists erased successfully!")
            self.success("Artists erased successfully!")
        else:
            self.status_sb.showMessage("An error occurred during the erase process :(")
            self.error("An error occurred during the erase process :(")
        self.get_items()

    def erase_albums(self):
        if not self.warning("This action will delete all the selected liked albums. Are you sure you wanna continue?"):
            return
        selected_items = self.list_l.selectedItems()
        if not selected_items:
            self.status_sb.showMessage("Select at least one album first!")
            return
        selected_items[:] = [item.data(32) for item in selected_items]
        self.clear_thread_connections()
        self.thread.started.connect(partial(self.spotipy_handler.erase_user_saved_albums, selected_items))
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.result_erase_albums)
        self.thread.start()

    def result_erase_albums(self, result):
        if result:
            self.status_sb.showMessage("Albums erased successfully!")
            self.success("Albums erased successfully!")
        else:
            self.status_sb.showMessage("An error occurred during the erase process :(")
            self.error("An error occurred during the erase process :(")
        self.get_items()

    def erase_shows(self):
        if not self.warning("This action will delete all the selected liked podcasts. Are you sure you wanna continue?"):
            return
        selected_items = self.list_l.selectedItems()
        if not selected_items:
            self.status_sb.showMessage("Select at least one podcasts first!")
            return
        selected_items[:] = [item.data(32) for item in selected_items]
        self.clear_thread_connections()
        self.thread.started.connect(partial(self.spotipy_handler.erase_user_saved_shows, selected_items))
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.result_erase_shows)
        self.thread.start()

    def result_erase_shows(self, result):
        if result:
            self.status_sb.showMessage("Podcasts erased successfully!")
            self.success("Podcasts erased successfully!")
        else:
            self.status_sb.showMessage("An error occurred during the erase process :(")
            self.error("An error occurred during the erase process :(")
        self.get_items()

    def select_all(self, select):
        if select:
            self.list_l.selectAll()
        else:
            self.list_l.clearSelection()

    def warning(self, msg):
        ret = self.msg_box.warning(self, 'Warning', msg, self.msg_box.Yes | self.msg_box.No)
        if ret == self.msg_box.Yes:
            return True
        else:
            return False

    def success(self, msg):
        self.msg_box.information(self, 'Success', msg)
    
    def error(self, msg):
        self.msg_box.critical(self, 'Error', msg)

    def open_about(self):
        self.about = QtWidgets.QMessageBox()
        self.about.setIconPixmap(QtGui.QPixmap(":/icon/icon.png"))
        self.about.setText("SpotyEraser\n\nFrancisco Maurino - 2021\n\nhttps://github.com/Laikos38")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icon/icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.about.setWindowIcon(icon)
        self.about.exec_()

    def update_progress(self, msg):
        self.status_sb.showMessage(msg)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()