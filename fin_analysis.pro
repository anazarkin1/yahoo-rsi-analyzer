#-------------------------------------------------
#
# Project created by QtCreator 2015-03-19T20:49:20
#
#-------------------------------------------------

QT       += core gui sql network script

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

TARGET = fin_analysis
TEMPLATE = app


SOURCES += main.cpp\
        mainwindow.cpp \
    maindatabase.cpp

HEADERS  += mainwindow.h

FORMS    += mainwindow.ui
