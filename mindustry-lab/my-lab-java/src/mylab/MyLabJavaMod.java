package mylab;

import mindustry.mod.Mod;

public class MyLabJavaMod extends Mod {

    public MyLabJavaMod() {
        System.out.println("[MyLabJava] mod loaded");
    }

    @Override
    public void loadContent() {
        // 方块本体由 content/blocks/regen-wall.hjson 声明，
        // 其中 type: mylab.RegenWall 会实例化本包里的自定义类
    }
}
