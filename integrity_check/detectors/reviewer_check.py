class ReviewerCheckDetector(BaseDetector):
    detector_name = "reviewer_check"

    def should_run(self, ctx) -> bool:
        return False  # 无投稿系统审稿人数据，不可用