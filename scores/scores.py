from PyQt5.QtCore import pyqtSignal, QObject, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QGridLayout, QLabel, \
	QGraphicsScene, QGraphicsPixmapItem, QGraphicsView
from PyQt5.QtChart import QChart, QChartView, QPieSeries, QPieSlice
from PyQt5.QtGui import QPainter, QColor, QBrush, QPalette, QFont, QPixmap


def main():
	app = QApplication( [ ] )
	main_window = MainWindow()
	main_window.setStyleSheet( open( "style.qss", "r" ).read() )
	main_window.showMaximized()
	app.exec_()


class Player( QObject ):
	score_added = pyqtSignal( int )
	score_subtracted = pyqtSignal( int )

	def __init__( self, name, color ):
		QObject.__init__( self )
		self.score = 0
		self.name = name
		self.color = color

	def add_score( self, score: int ):
		self.score += score
		self.score_added.emit( score )

	def subtract_score( self, score: int ):
		self.score -= score
		self.score_subtracted.emit( score )


player_1 = Player( "Lukas", QColor( "#FFE014" ) )
player_2 = Player( "Eileen", QColor( "#2c7822" ) )
remaining_points_color = QColor( "#000000" )


class MainWindow( QWidget ):
	def __init__( self ):
		QWidget.__init__( self )

		self.layout = QVBoxLayout()
		self.points_layout = QHBoxLayout()

		self.title_text = TitleText()

		self.score_cake = ScoreCake( (player_1, player_2) )

		self.score_container_1 = ScorePanel( player_1 )
		self.score_container_2 = ScorePanel( player_2 )

		self.points_layout.addWidget( self.score_container_1 )
		self.points_layout.addWidget( self.score_container_2 )

		self.layout.addWidget( self.title_text )
		self.layout.addWidget( self.score_cake )
		self.layout.addLayout( self.points_layout )
		self.layout.setAlignment( self.title_text, Qt.AlignCenter )

		self.setLayout( self.layout )


class TitleText( QGraphicsView ):
	def __init__( self ):
		self.scene = QGraphicsScene()
		QGraphicsView.__init__( self, self.scene )
		self.pix_map_item = QGraphicsPixmapItem( QPixmap( "TitleText.png" ) )
		self.pix_map_item.scale()
		self.scene.addItem( self.pix_map_item )
		self.size = self.pix_map_item.pixmap().size()
		self.setMaximumSize( self.size )


class ScoreCake( QWidget ):
	def __init__( self, players ):
		QWidget.__init__( self )
		self.players = players

		player_1.score_added.connect( self.update_cake )
		player_1.score_subtracted.connect( self.update_cake )
		player_2.score_added.connect( self.update_cake )
		player_2.score_subtracted.connect( self.update_cake )

		self.cake = self.make_cake()

		self.layout = QVBoxLayout()
		self.layout.setContentsMargins( 0, 0, 0, 0 )
		self.layout.setSpacing( 0 )
		self.layout.addWidget( self.cake )
		self.setLayout( self.layout )

	def make_cake( self ):
		score_1 = self.players[ 0 ].score
		score_2 = self.players[ 1 ].score
		series = QPieSeries()
		free_score = 120 - score_1 - score_2
		series.append( f"{free_score}", free_score )
		series.append( f"{score_1}", score_1 )
		series.append( f"{score_2}", score_2 )
		series.setPieStartAngle( 3 * score_2 )
		series.setPieEndAngle( 3 * score_2 + 360 )

		slices = series.slices()
		for slice in slices:
			slice.setLabelVisible( True )
			if slice.angleSpan() < 45:
				slice.setLabelPosition( QPieSlice.LabelPosition.LabelInsideNormal )
			elif slice.angleSpan() < 90:
				slice.setLabelPosition( QPieSlice.LabelPosition.LabelInsideTangential )
			else:
				slice.setLabelPosition( QPieSlice.LabelPosition.LabelInsideHorizontal )
			slice.setLabelColor( QColor( "#00000" ) )
			slice.setLabelFont( QFont( "Fira Sans", 60, weight=QFont.Weight.Black ) )
			slice.setBorderWidth( 0 )

		slices[ 0 ].setLabelPosition( QPieSlice.LabelPosition.LabelInsideHorizontal )
		if score_1 < 10:
			slices[ 1 ].setLabelFont( QFont( "Fira Sans", score_1 * 6, weight=QFont.Weight.Black ) )
		if score_2 < 10:
			slices[ 2 ].setLabelFont( QFont( "Fira Sans", score_2 * 6, weight=QFont.Weight.Black ) )

		slices[ 0 ].setLabelColor( QColor( "#FFFFFF" ) )
		slices[ 0 ].setColor( remaining_points_color )
		slices[ 1 ].setColor( player_1.color )
		slices[ 2 ].setColor( player_2.color )

		chart = QChart()
		chart.legend().hide()
		chart.addSeries( series )
		chart.createDefaultAxes()
		chart.setBackgroundVisible( False )

		chart.setContentsMargins( -120, -120, -120, -120 )
		chart.layout().setContentsMargins( 0, 0, 0, 0 )

		chart_view = QChartView( chart )
		chart_view.setRenderHint( QPainter.Antialiasing )

		return chart_view

	def update_cake( self ):
		self.layout.removeWidget( self.cake )
		self.cake.deleteLater()
		self.cake = self.make_cake()
		self.layout.addWidget( self.cake )


class ScorePanel( QWidget ):
	def __init__( self, player: Player ):
		QWidget.__init__( self )

		self.name = player.name

		self.layout = QVBoxLayout()
		self.layout.setSpacing( 0 )
		self.layout.setContentsMargins( 0, 0, 0, 0 )

		self.name_label = QLabel( self.name )
		self.name_label.setStyleSheet( f"background-color: {player.color.name()};" )
		self.score_buttons = ScoreButtonContainer( player )

		self.layout.addWidget( self.name_label )
		self.layout.addWidget( self.score_buttons )

		self.setLayout( self.layout )


class ScoreButtonContainer( QWidget ):
	def __init__( self, player: Player ):
		QWidget.__init__( self )
		self.layout = QGridLayout()
		self.layout.setSpacing( 0 )
		self.layout.setContentsMargins( 0, 0, 0, 0 )

		for i in range( 15 ):
			button = ScoreButton( player, i + 1 )
			self.layout.addWidget( button, int( i / 5 ), i % 5 )
			callback = self.make_button_callback( button, player, i + 1 )
			button.clicked.connect( callback )

		self.setLayout( self.layout )

		self.player = player
		opponent = player_1 if player == player_2 else player_2
		opponent.score_added.connect( self.handle_opponent )

	def handle_opponent( self, score: int ):
		button = self.layout.itemAt( score - 1 ).widget()

		if button.state == 1:
			button.player.subtract_score( score )

		button.change_state( -1 )

	@staticmethod
	def make_button_callback( button, player: Player, score: int ):
		def callback():
			if button.state == 0 or button.state == -1:
				player.add_score( score )
				button.change_state( 1 )

		return callback


class ScoreButton( QPushButton ):
	def __init__( self, player: Player, num: int ):
		QPushButton.__init__( self, str( num ) )
		self.num = num
		self.state = 0
		self.player = player

	def change_state( self, new_state: int ):
		self.state = new_state
		self.setProperty( "state", str( self.state ) )
		self.style().unpolish( self )
		self.ensurePolished()


main()
