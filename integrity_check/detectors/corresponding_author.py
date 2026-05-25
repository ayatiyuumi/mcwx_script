class CorrespondingAuthorDetector(BaseDetector):
    detector_name = "corresponding_author"

    def should_run(self, ctx) -> bool:
        return False  # 无投稿系统数据,依赖投稿系统数据，原型不可用