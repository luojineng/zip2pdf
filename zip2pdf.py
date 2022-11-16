import os 
import sys
from time import sleep
import zipfile
from pywinauto.application import Application
from colorama import init 
from traceback import print_exc
from pywinauto.timings import Timings
import subprocess

# from pywinauto.keyboard import send_keys

# ok TODO 加密压缩包解密
# rar解密支持
# 多个压缩包批量解密


def zip2pdg(filename):
    # 非zip压缩文件，退出
    if not zipfile.is_zipfile(filename):
        print(filename+" \033[0;31;40m非ZIP压缩包！\033[0m\n")
        sys.exit()

    with zipfile.ZipFile(filename) as zf:
        # ok TODO 压缩包加密，退出 https://stackoverflow.com/a/12038744/10628285
        zinfo=zf.infolist()
        pwds=None
        if (zinfo[1].flag_bits & 0x1) or (zinfo[2].flag_bits & 0x1):
            print(filename+" \033[0;31;40m是加密压缩包！\033[0m\n")
            # 常用密码 https://readfree.net/bbs/forum.php?mod=viewthread&tid=5898121&extra=page%3D1
            # pwds=['52gv','28zrs']
            py_dirname= os.path.dirname(os.path.abspath(sys.argv[0]))
            pwd_path=py_dirname+"\\passwords\\passwords.txt"
            with open(pwd_path,'r',encoding='utf8') as f:
                pwds=f.readlines()
            # sys.exit()

        # ok TODO 压缩文件是为目录,直接解压
        path=os.path.dirname(filename)
        if not (zinfo[0].is_dir() or len(zinfo[0].filename.split('/'))!=1):
            if not os.path.exists(filename.strip(".zip")):
                os.mkdir(filename.strip(".zip"))
            path=filename.strip(".zip")

        # ok TODO 解决解压目录中文乱码问题 https://stackoverflow.com/a/54111461/10628285
        true_pwd=None
        for member in zinfo:
            member.filename = member.filename.encode('cp437').decode('gbk')
            if pwds and (not true_pwd):
                for pwd in pwds:
                    pwd_strip=pwd.rstrip("\n")
                    try:
                        extract_item=zf.extract(member,path,pwd_strip.encode('gbk'))
                        # 目录是没有密码的
                        if os.path.isfile(extract_item):
                            true_pwd=pwd_strip
                            print(filename+" \033[0;31;40m解压密码为：\033[0m\033[0;32;40m"+true_pwd+"\033[0m\n")
                            break
                    except NotImplementedError:
                        print(filename+" \033[0;31;40m加密方式为AES-256,不支持,需要手动解压！\033[0m\n")
                        zf.close()
                        sys.exit(0)
                    except:
                        if pwd ==pwds[-1]:
                            print(filename+" \033[0;31;40m解密失败,需要手动解压！\033[0m\n")
                            zf.close()
                            sys.exit(0)
                        pass
            if not true_pwd:
                zf.extract(member,path)
        if true_pwd:
            # TODO 7z.exe
            zip_path=py_dirname+"\\7-Zip\\7z.exe"
            completed = subprocess.run([zip_path,'x',filename,'-o'+path,'-p'+true_pwd,'-y'])
            if completed.returncode==0:
                print("\n"+filename+" \033[0;31;40m解压成功！\033[0m\n")


        # 返回pdg目录名
        return (path+"\\"+zinfo[0].filename.split('/')[0] if path==os.path.dirname(filename) else filename.strip(".zip"))


# TODO PDG转PDF

def pdg2pdf(dirname):
    # TODO file_name解析
    py_dirname= os.path.dirname(os.path.abspath(sys.argv[0]))
    path = py_dirname+ "\\Pdg2Pic\\Pdg2Pic.exe"
    app = Application(backend='uia').start(path)
    # 连接软件的主窗口
    dlg_spec = app.window(title_re='Pdg2Pic*', class_name_re='#32770*')
    # 设置焦点，使其处于活动状态
    dlg_spec.set_focus()

    # 选择pdg目录，send_keys('1')
    dlg_spec['Button2'].click()

    # 选择桌面，以便确定
    dlg_spec['TreeItem'].click_input()

    # 设置pdg目录
    dlg_spec['文件夹(F):Edit'].set_edit_text(dirname)
    dlg_spec['确定Button'].click()
    # sleep(2)
    # dlg_spec.print_control_identifiers()
    # sleep(60)
    # Timings.fast()

    # ok_dialog = dlg_spec.child_window(title='格式统计')
    # ok_dialog.wait("ready",5,0.5)
    # ok_dialog.print_control_identifiers()
    # sleep(60)
    dlg_spec['OKButton'].click_input()
    # TODO 转换性能问题
    dlg_spec['4、开始转换Button'].click()
    # ok TODO 转换需要时间，怎么判断？

    # complete_dialog = dlg_spec.child_window(title='Pdg2Pic')

    while dlg_spec['Static23'].window_text()[:5]=='存盘...':
        break

    # 转换完毕
    # dlg_spec['OKButton'].wait("ready",5,0.5)
    dlg_spec['OKButton'].click_input()

    return dlg_spec
    # 测试
    # dlg_spec.close()    
    # send_keys('4')
    # dlg_spec.print_control_identifiers()
    # print(dlg_spec['Static23'].window_text()[:5]+'\n')



if __name__ == '__main__':
    filename=sys.argv[1]
    i=0
    init()
    while True:
        try:
            if os.path.isfile(filename):
                dirname=zip2pdg(filename)
                print("\n\n"+filename+" \033[0;32;40m已解压成PDG!\033[0m")
            else:
                dirname=filename
            dlg_spec=pdg2pdf(dirname)
            # 关闭PDG2Pic
            sleep(1)
            dlg_spec['Close2'].click()
            print("\n\n"+filename+" \033[0;32;40m已转成PDF!\033[0m\n\n")
        except:
            print('\n')
            print_exc()
            print("\n\033[0;32;40m程序运行有问题，记录出错信息，按enter键退出\033[0m\n")
        i=i+1
        print("\033[0;31;40m重开+"+str(i)+"\033[0m\n")
        dirname=filename=None
        # 重复Input,cmd会自动加空格，然后出现莫名Bug
        filename=input("请输入zip文件或pdg目录：").replace("\"","").rstrip(' ')










