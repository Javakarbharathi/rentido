"""
Rentido config package.
Initializes PyMySQL as the MySQLdb driver for Django.
"""
import pymysql

pymysql.install_as_MySQLdb()
