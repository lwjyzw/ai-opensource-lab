package mylab;

import mindustry.world.blocks.defense.Wall;

/**
 * 再生护墙：每 tick 缓慢自愈。
 *
 * 核心套路（Mindustry Java Mod 最常见模式）：
 *   1. 继承原版 Block（这里是 Wall），构造器里改属性（update = true 才会跑 updateTile）
 *   2. 定义内部类 <类名>Build 继承原版的 Build 类，覆写 updateTile 写自定义行为
 *   3. hjson 里写 type: 包名.类名 绑定，其余字段照常用 hjson 配置
 */
public class RegenWall extends Wall {

    // 每 tick 回复量（原版心脏修复塔约每秒回 1.2% —— 我们设成慢速常驻）
    public float healPercentPerSecond = 0.4f;

    public RegenWall(String name) {
        super(name);
        update = true;          // 没有这个 Build 的 updateTile 不会被调用
        solid = true;
        hasShadow = true;
    }

    public class RegenWallBuild extends WallBuild {

        @Override
        public void updateTile() {
            if (damaged()) {
                float amount = maxHealth * healPercentPerSecond / 60f * delta();
                health(Math.min(maxHealth, health + amount));
            }
        }
    }
}
