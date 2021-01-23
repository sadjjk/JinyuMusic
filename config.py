class Config:
    pass


class DevelopmentConfig(Config):
    """开发模式的配置信息"""
    DEBUG = True


class ProductionConfig(Config):
    """生产环境配置信息"""
    pass


CONFIG_MAP = {
    "develop": DevelopmentConfig,
    "product": ProductionConfig
}
