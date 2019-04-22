from PyQt5.QtWidgets import QTableWidgetItem

class tableModel():
	def __init__(self, table, columns, headers):
		self.table = table
		self.table.setColumnCount(columns)
		self.table.setHorizontalHeaderLabels(headers)

	def insert(self, items):
		self.table.insertRow(self.table.rowCount())
		for index, item in enumerate(items):
			self.table.setItem(self.table.rowCount()-1, index, QTableWidgetItem(str(item)))

	def clear(self):
		self.table.clear()

