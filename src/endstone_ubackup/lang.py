import os
import json


def load_langs(lang_dir: str) -> dict:
    lang_en_US_file_path = os.path.join(lang_dir, 'en_US.json')
    lang_zh_CN_file_path = os.path.join(lang_dir, 'zh_CN.json')

    if not os.path.exists(lang_en_US_file_path):
        with open(lang_en_US_file_path, 'w', encoding='utf-8') as f:
            en_US = {
                'time_expense': 'Time expense',
                'size': 'Size',
                'back': 'Back to previous',
                
                'main_form.title': 'U-Backup - main form',
                'main_form.content': 'Please select a function...',
                'main_form.button.manual_backup': 'Manual backup',
                'main_form.button.reload_configurations': 'Reload configurations',
                'main_form.button.close': 'Close',
                'main_form.button.back_to_zx_ui': 'Back to menu',

                'manual_backup.message.fail': 'Failed to start a manual backup',
                'manual_backup.message.fail.reason1': 'there is already a ongoing backup...',
                'manual_backup.message.fail.reason2': 'there is no enough disk space...',
                'manual_backup.broadcast.start': 'A manual backup has started...',
                'manual_backup.broadcast.complete': 'A manual backup has completed...',

                'schedule_backup.broadcast.fail': 'Failed to start a schedule backup[{0}]',
                'schedule_backup.broadcast.fail.reason1': 'there is already a ongoing backup...',
                'schedule_backup.broadcast.fail.reason2': 'there is no enough disk space...',
                'schedule_backup.broadcast.start': 'A schedule backup[{0}] has started...',
                'schedule_backup.broadcast.complete': 'A schedule backup[{0}] has completed...',

                'reload_configurations_from.title': 'Reload configurations',
                'reload_configurations_from.content1': 'Current schedule backup time of the server',
                'reload_configurations_from.content2': 'Current max number of backups retained by the server',
                'reload_configurations_from.content3': 'Server owner should firstly edit and save config.json and then click the "reload" button here to reload configurations...',
                'reload_configurations_from.button.reload': 'Reload',

                'reload_configurations.message.success': 'Successfully reload configurations...'
            }

            json_str = json.dumps(
                en_US,
                indent=4,
                ensure_ascii=False
            )

            f.write(json_str)

    if not os.path.exists(lang_zh_CN_file_path):
        with open(lang_zh_CN_file_path, 'w', encoding='utf-8') as f:
            zh_CN = {
                'time_expense': '耗时',
                'size': '大小',
                'back': '返回',

                'main_form.title': 'U-Backup - 主表单',
                'main_form.content': '请选择操作...',
                'main_form.button.manual_backup': '手动备份',
                'main_form.button.reload_configurations': '重载配置文件',
                'main_form.button.close': '关闭',
                'main_form.button.back_to_zx_ui': '反回',

                'manual_backup.message.fail': '手动备份开始失败',
                'manual_backup.message.fail.reason1': '已经有一个正在进行的备份了...',
                'manual_backup.message.fail.reason2': '磁盘空间不足...',
                'manual_backup.broadcast.start': '手动备份已开始...',
                'manual_backup.broadcast.complete': '手动备份已完成...',

                'schedule_backup.broadcast.fail': '[{0}]计划备份开始失败',
                'schedule_backup.broadcast.fail.reason1': '已经有一个正在进行的备份了...',
                'schedule_backup.broadcast.fail.reason2': '磁盘空间不足...',
                'schedule_backup.broadcast.start': '[{0}]计划备份已开始...',
                'schedule_backup.broadcast.complete': '[{0}]计划备份已完成...',

                'reload_configurations_from.title': '重载配置文件',
                'reload_configurations_from.content1': '当前服务器的计划备份时间',
                'reload_configurations_from.content2': '当前服务器保留的最大备份数量',
                'reload_configurations_from.content3': '服主应先编辑并保存 config.json, 然后点击 "重载" 按钮来重载配置文件...',
                'reload_configurations_from.button.reload': '重载',

                'reload_configurations.message.success': '重载配置文件成功...'

            }

            json_str = json.dumps(
                zh_CN,
                indent=4,
                ensure_ascii=False
            )

            f.write(json_str)

    langs = {}

    for lang in os.listdir(lang_dir):
        lang_name = lang.strip('.json')

        lang_file_path = os.path.join(lang_dir, lang)

        with open(lang_file_path, 'r', encoding='utf-8') as f:
            langs[lang_name] = json.loads(f.read())

    return langs





