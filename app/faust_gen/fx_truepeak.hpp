/* ------------------------------------------------------------
name: "fx_truepeak"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn FxTruepeak -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __FxTruepeak_H__
#define  __FxTruepeak_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS FxTruepeak
#endif

#ifdef __APPLE__ 
#define exp10f __exp10f
#define exp10 __exp10
#endif

#if defined(_WIN32)
#define RESTRICT __restrict
#else
#define RESTRICT __restrict__
#endif


class FxTruepeak : public dsp {
	
 private:
	
	FAUSTFLOAT fHslider0;
	int IOTA0;
	float fVec0[256];
	float fVec1[256];
	int fSampleRate;
	float fConst0;
	float fRec1[2];
	float fVec2[3];
	float fVec3[5];
	float fVec4[9];
	float fVec5[32];
	float fVec6[64];
	float fVec7[128];
	float fVec8[2];
	float fVec9[3];
	float fVec10[5];
	float fVec11[9];
	float fVec12[32];
	float fVec13[64];
	float fVec14[128];
	float fVec15[256];
	float fVec16[256];
	float fRec0[2];
	float fVec17[3];
	float fVec18[5];
	float fVec19[9];
	float fVec20[32];
	float fVec21[64];
	float fVec22[128];
	float fVec23[2];
	float fVec24[3];
	float fVec25[5];
	float fVec26[9];
	float fVec27[32];
	float fVec28[64];
	float fVec29[128];
	
 public:
	FxTruepeak() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/parallelOp:author", "Bart Brouns");
		m->declare("basics.lib/parallelOp:copyright", "Copyright (c) 2020 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/parallelOp:licence", "GPL-3.0");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn FxTruepeak -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("filename", "fx_truepeak.dsp");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "fx_truepeak");
		m->declare("platform.lib/name", "Generic Platform Library");
		m->declare("platform.lib/version", "1.3.0");
		m->declare("signals.lib/name", "Faust Signal Routing Library");
		m->declare("signals.lib/version", "1.5.0");
	}

	virtual int getNumInputs() {
		return 2;
	}
	virtual int getNumOutputs() {
		return 2;
	}
	
	static void classInit(int sample_rate) {
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::exp(-(12.5f / std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)))));
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(-1.0f);
	}
	
	virtual void instanceClear() {
		IOTA0 = 0;
		for (int l0 = 0; l0 < 256; l0 = l0 + 1) {
			fVec0[l0] = 0.0f;
		}
		for (int l1 = 0; l1 < 256; l1 = l1 + 1) {
			fVec1[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			fRec1[l2] = 0.0f;
		}
		for (int l3 = 0; l3 < 3; l3 = l3 + 1) {
			fVec2[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 5; l4 = l4 + 1) {
			fVec3[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 9; l5 = l5 + 1) {
			fVec4[l5] = 0.0f;
		}
		for (int l6 = 0; l6 < 32; l6 = l6 + 1) {
			fVec5[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 64; l7 = l7 + 1) {
			fVec6[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 128; l8 = l8 + 1) {
			fVec7[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			fVec8[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 3; l10 = l10 + 1) {
			fVec9[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 5; l11 = l11 + 1) {
			fVec10[l11] = 0.0f;
		}
		for (int l12 = 0; l12 < 9; l12 = l12 + 1) {
			fVec11[l12] = 0.0f;
		}
		for (int l13 = 0; l13 < 32; l13 = l13 + 1) {
			fVec12[l13] = 0.0f;
		}
		for (int l14 = 0; l14 < 64; l14 = l14 + 1) {
			fVec13[l14] = 0.0f;
		}
		for (int l15 = 0; l15 < 128; l15 = l15 + 1) {
			fVec14[l15] = 0.0f;
		}
		for (int l16 = 0; l16 < 256; l16 = l16 + 1) {
			fVec15[l16] = 0.0f;
		}
		for (int l17 = 0; l17 < 256; l17 = l17 + 1) {
			fVec16[l17] = 0.0f;
		}
		for (int l18 = 0; l18 < 2; l18 = l18 + 1) {
			fRec0[l18] = 0.0f;
		}
		for (int l19 = 0; l19 < 3; l19 = l19 + 1) {
			fVec17[l19] = 0.0f;
		}
		for (int l20 = 0; l20 < 5; l20 = l20 + 1) {
			fVec18[l20] = 0.0f;
		}
		for (int l21 = 0; l21 < 9; l21 = l21 + 1) {
			fVec19[l21] = 0.0f;
		}
		for (int l22 = 0; l22 < 32; l22 = l22 + 1) {
			fVec20[l22] = 0.0f;
		}
		for (int l23 = 0; l23 < 64; l23 = l23 + 1) {
			fVec21[l23] = 0.0f;
		}
		for (int l24 = 0; l24 < 128; l24 = l24 + 1) {
			fVec22[l24] = 0.0f;
		}
		for (int l25 = 0; l25 < 2; l25 = l25 + 1) {
			fVec23[l25] = 0.0f;
		}
		for (int l26 = 0; l26 < 3; l26 = l26 + 1) {
			fVec24[l26] = 0.0f;
		}
		for (int l27 = 0; l27 < 5; l27 = l27 + 1) {
			fVec25[l27] = 0.0f;
		}
		for (int l28 = 0; l28 < 9; l28 = l28 + 1) {
			fVec26[l28] = 0.0f;
		}
		for (int l29 = 0; l29 < 32; l29 = l29 + 1) {
			fVec27[l29] = 0.0f;
		}
		for (int l30 = 0; l30 < 64; l30 = l30 + 1) {
			fVec28[l30] = 0.0f;
		}
		for (int l31 = 0; l31 < 128; l31 = l31 + 1) {
			fVec29[l31] = 0.0f;
		}
	}
	
	virtual void init(int sample_rate) {
		classInit(sample_rate);
		instanceInit(sample_rate);
	}
	
	virtual void instanceInit(int sample_rate) {
		instanceConstants(sample_rate);
		instanceResetUserInterface();
		instanceClear();
	}
	
	virtual FxTruepeak* clone() {
		return new FxTruepeak();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("fx_truepeak");
		ui_interface->addHorizontalSlider("ceiling", &fHslider0, FAUSTFLOAT(-1.0f), FAUSTFLOAT(-12.0f), FAUSTFLOAT(0.0f), FAUSTFLOAT(0.1f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* input0 = inputs[0];
		FAUSTFLOAT* input1 = inputs[1];
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fHslider0);
		float fSlow1 = std::pow(1e+01f, 0.05f * (fSlow0 + -0.1f));
		float fSlow2 = std::pow(1e+01f, 0.05f * (fSlow0 + -1.0f));
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			float fTemp0 = float(input0[i0]);
			fVec0[IOTA0 & 255] = fTemp0;
			float fTemp1 = fVec0[(IOTA0 - 15) & 255];
			float fTemp2 = fVec0[(IOTA0 - 16) & 255];
			float fTemp3 = fVec0[(IOTA0 - 31) & 255];
			float fTemp4 = fVec0[(IOTA0 - 29) & 255];
			float fTemp5 = fVec0[(IOTA0 - 27) & 255];
			float fTemp6 = fVec0[(IOTA0 - 25) & 255];
			float fTemp7 = fVec0[(IOTA0 - 23) & 255];
			float fTemp8 = fVec0[(IOTA0 - 21) & 255];
			float fTemp9 = fVec0[(IOTA0 - 19) & 255];
			float fTemp10 = fVec0[(IOTA0 - 17) & 255];
			float fTemp11 = fVec0[(IOTA0 - 14) & 255];
			float fTemp12 = fVec0[(IOTA0 - 12) & 255];
			float fTemp13 = fVec0[(IOTA0 - 10) & 255];
			float fTemp14 = fVec0[(IOTA0 - 8) & 255];
			float fTemp15 = fVec0[(IOTA0 - 6) & 255];
			float fTemp16 = fVec0[(IOTA0 - 4) & 255];
			float fTemp17 = fVec0[(IOTA0 - 2) & 255];
			float fTemp18 = fVec0[(IOTA0 - 28) & 255];
			float fTemp19 = fVec0[(IOTA0 - 30) & 255];
			float fTemp20 = fVec0[(IOTA0 - 26) & 255];
			float fTemp21 = fVec0[(IOTA0 - 24) & 255];
			float fTemp22 = fVec0[(IOTA0 - 22) & 255];
			float fTemp23 = fVec0[(IOTA0 - 20) & 255];
			float fTemp24 = fVec0[(IOTA0 - 18) & 255];
			float fTemp25 = fVec0[(IOTA0 - 13) & 255];
			float fTemp26 = fVec0[(IOTA0 - 11) & 255];
			float fTemp27 = fVec0[(IOTA0 - 9) & 255];
			float fTemp28 = fVec0[(IOTA0 - 7) & 255];
			float fTemp29 = fVec0[(IOTA0 - 5) & 255];
			float fTemp30 = fVec0[(IOTA0 - 3) & 255];
			float fTemp31 = fVec0[(IOTA0 - 1) & 255];
			float fTemp32 = float(input1[i0]);
			fVec1[IOTA0 & 255] = fTemp32;
			float fTemp33 = fVec1[(IOTA0 - 15) & 255];
			float fTemp34 = fVec1[(IOTA0 - 16) & 255];
			float fTemp35 = fVec1[(IOTA0 - 31) & 255];
			float fTemp36 = fVec1[(IOTA0 - 29) & 255];
			float fTemp37 = fVec1[(IOTA0 - 27) & 255];
			float fTemp38 = fVec1[(IOTA0 - 25) & 255];
			float fTemp39 = fVec1[(IOTA0 - 23) & 255];
			float fTemp40 = fVec1[(IOTA0 - 21) & 255];
			float fTemp41 = fVec1[(IOTA0 - 19) & 255];
			float fTemp42 = fVec1[(IOTA0 - 17) & 255];
			float fTemp43 = fVec1[(IOTA0 - 14) & 255];
			float fTemp44 = fVec1[(IOTA0 - 12) & 255];
			float fTemp45 = fVec1[(IOTA0 - 10) & 255];
			float fTemp46 = fVec1[(IOTA0 - 8) & 255];
			float fTemp47 = fVec1[(IOTA0 - 6) & 255];
			float fTemp48 = fVec1[(IOTA0 - 4) & 255];
			float fTemp49 = fVec1[(IOTA0 - 2) & 255];
			float fTemp50 = fVec1[(IOTA0 - 28) & 255];
			float fTemp51 = fVec1[(IOTA0 - 30) & 255];
			float fTemp52 = fVec1[(IOTA0 - 26) & 255];
			float fTemp53 = fVec1[(IOTA0 - 24) & 255];
			float fTemp54 = fVec1[(IOTA0 - 22) & 255];
			float fTemp55 = fVec1[(IOTA0 - 20) & 255];
			float fTemp56 = fVec1[(IOTA0 - 18) & 255];
			float fTemp57 = fVec1[(IOTA0 - 13) & 255];
			float fTemp58 = fVec1[(IOTA0 - 11) & 255];
			float fTemp59 = fVec1[(IOTA0 - 9) & 255];
			float fTemp60 = fVec1[(IOTA0 - 7) & 255];
			float fTemp61 = fVec1[(IOTA0 - 5) & 255];
			float fTemp62 = fVec1[(IOTA0 - 3) & 255];
			float fTemp63 = fVec1[(IOTA0 - 1) & 255];
			fRec1[0] = std::max<float>(1.0f - fSlow2 / std::max<float>(fSlow2, std::max<float>(std::max<float>(std::max<float>(std::fabs(fTemp1), std::fabs(fTemp2)), std::max<float>(std::fabs(0.0014147608f * fTemp31 + 0.0029899369f * fTemp30 + 0.006525907f * fTemp29 + 0.0128541235f * fTemp28 + 0.023639692f * fTemp27 + 0.043584947f * fTemp26 + 0.09441519f * fTemp25 + 0.89973646f * fTemp1 + 0.29991215f * fTemp2 + 0.07724879f * fTemp24 + 0.038997058f * fTemp23 + 0.021888603f * fTemp22 + 0.012119602f * fTemp21 + 0.0062223766f * fTemp20 + 0.0013668028f * fTemp19 + 0.0028726843f * fTemp18 - (0.001995664f * fTemp17 + 0.0044707493f * fTemp16 + 0.009268237f * fTemp15 + 0.017517908f * fTemp14 + 0.03189086f * fTemp13 + 0.061675683f * fTemp12 + 0.17656787f * fTemp11 + 0.1261199f * fTemp10 + 0.05345226f * fTemp9 + 0.029117743f * fTemp8 + 0.01638772f * fTemp7 + 0.008792942f * fTemp6 + 0.004280505f * fTemp5 + 0.0019230944f * fTemp4 + 0.0011827738f * fTemp0 + 0.0011452254f * fTemp3)), std::max<float>(std::fabs(0.0019660336f * (fTemp19 + fTemp31) + 0.004143326f * (fTemp18 + fTemp30) + 0.009008168f * (fTemp20 + fTemp29) + 0.017641623f * (fTemp21 + fTemp28) + 0.03214175f * (fTemp22 + fTemp27) + 0.058206834f * (fTemp23 + fTemp26) + 0.6361307f * (fTemp2 + fTemp1) + 0.12015598f * (fTemp24 + fTemp25) - (0.002769686f * (fTemp4 + fTemp17) + 0.006184378f * (fTemp5 + fTemp16) + 0.012760753f * (fTemp6 + fTemp15) + 0.023945283f * (fTemp7 + fTemp14) + 0.04304512f * (fTemp8 + fTemp13) + 0.20806137f * (fTemp10 + fTemp11) + 0.08098234f * (fTemp9 + fTemp12) + 0.0016455112f * (fTemp0 + fTemp3))), std::fabs(0.0013668028f * fTemp31 + 0.0028726843f * fTemp30 + 0.0062223766f * fTemp29 + 0.012119602f * fTemp28 + 0.021888603f * fTemp27 + 0.038997058f * fTemp26 + 0.07724879f * fTemp25 + 0.29991215f * fTemp1 + 0.89973646f * fTemp2 + 0.09441519f * fTemp24 + 0.043584947f * fTemp23 + 0.023639692f * fTemp22 + 0.0128541235f * fTemp21 + 0.006525907f * fTemp20 + 0.0014147608f * fTemp19 + 0.0029899369f * fTemp18 - (0.0019230944f * fTemp17 + 0.004280505f * fTemp16 + 0.008792942f * fTemp15 + 0.01638772f * fTemp14 + 0.029117743f * fTemp13 + 0.05345226f * fTemp12 + 0.1261199f * fTemp11 + 0.17656787f * fTemp10 + 0.061675683f * fTemp9 + 0.03189086f * fTemp8 + 0.017517908f * fTemp7 + 0.009268237f * fTemp6 + 0.0044707493f * fTemp5 + 0.001995664f * fTemp4 + 0.0011452254f * fTemp0 + 0.0011827738f * fTemp3))))), std::max<float>(std::max<float>(std::fabs(fTemp33), std::fabs(fTemp34)), std::max<float>(std::fabs(0.0014147608f * fTemp63 + 0.0029899369f * fTemp62 + 0.006525907f * fTemp61 + 0.0128541235f * fTemp60 + 0.023639692f * fTemp59 + 0.043584947f * fTemp58 + 0.09441519f * fTemp57 + 0.89973646f * fTemp33 + 0.29991215f * fTemp34 + 0.07724879f * fTemp56 + 0.038997058f * fTemp55 + 0.021888603f * fTemp54 + 0.012119602f * fTemp53 + 0.0062223766f * fTemp52 + 0.0013668028f * fTemp51 + 0.0028726843f * fTemp50 - (0.001995664f * fTemp49 + 0.0044707493f * fTemp48 + 0.009268237f * fTemp47 + 0.017517908f * fTemp46 + 0.03189086f * fTemp45 + 0.061675683f * fTemp44 + 0.17656787f * fTemp43 + 0.1261199f * fTemp42 + 0.05345226f * fTemp41 + 0.029117743f * fTemp40 + 0.01638772f * fTemp39 + 0.008792942f * fTemp38 + 0.004280505f * fTemp37 + 0.0019230944f * fTemp36 + 0.0011827738f * fTemp32 + 0.0011452254f * fTemp35)), std::max<float>(std::fabs(0.0019660336f * (fTemp51 + fTemp63) + 0.004143326f * (fTemp50 + fTemp62) + 0.009008168f * (fTemp52 + fTemp61) + 0.017641623f * (fTemp53 + fTemp60) + 0.03214175f * (fTemp54 + fTemp59) + 0.058206834f * (fTemp55 + fTemp58) + 0.6361307f * (fTemp34 + fTemp33) + 0.12015598f * (fTemp56 + fTemp57) - (0.002769686f * (fTemp36 + fTemp49) + 0.006184378f * (fTemp37 + fTemp48) + 0.012760753f * (fTemp38 + fTemp47) + 0.023945283f * (fTemp39 + fTemp46) + 0.04304512f * (fTemp40 + fTemp45) + 0.20806137f * (fTemp42 + fTemp43) + 0.08098234f * (fTemp41 + fTemp44) + 0.0016455112f * (fTemp32 + fTemp35))), std::fabs(0.0013668028f * fTemp63 + 0.0028726843f * fTemp62 + 0.0062223766f * fTemp61 + 0.012119602f * fTemp60 + 0.021888603f * fTemp59 + 0.038997058f * fTemp58 + 0.07724879f * fTemp57 + 0.29991215f * fTemp33 + 0.89973646f * fTemp34 + 0.09441519f * fTemp56 + 0.043584947f * fTemp55 + 0.023639692f * fTemp54 + 0.0128541235f * fTemp53 + 0.006525907f * fTemp52 + 0.0014147608f * fTemp51 + 0.0029899369f * fTemp50 - (0.0019230944f * fTemp49 + 0.004280505f * fTemp48 + 0.008792942f * fTemp47 + 0.01638772f * fTemp46 + 0.029117743f * fTemp45 + 0.05345226f * fTemp44 + 0.1261199f * fTemp43 + 0.17656787f * fTemp42 + 0.061675683f * fTemp41 + 0.03189086f * fTemp40 + 0.017517908f * fTemp39 + 0.009268237f * fTemp38 + 0.0044707493f * fTemp37 + 0.001995664f * fTemp36 + 0.0011452254f * fTemp32 + 0.0011827738f * fTemp35))))))), fConst0 * fRec1[1]);
			float fTemp64 = std::max<float>(fRec1[0], fRec1[1]);
			fVec2[0] = fTemp64;
			float fTemp65 = std::max<float>(fTemp64, fVec2[2]);
			fVec3[0] = fTemp65;
			float fTemp66 = std::max<float>(fTemp65, fVec3[4]);
			fVec4[0] = fTemp66;
			float fTemp67 = std::max<float>(fTemp66, fVec4[8]);
			fVec5[IOTA0 & 31] = fTemp67;
			float fTemp68 = std::max<float>(fTemp67, fVec5[(IOTA0 - 16) & 31]);
			fVec6[IOTA0 & 63] = fTemp68;
			float fTemp69 = std::max<float>(fTemp68, fVec6[(IOTA0 - 32) & 63]);
			fVec7[IOTA0 & 127] = fTemp69;
			float fTemp70 = std::max<float>(-3.4028235e+38f, std::max<float>(fTemp69, fVec7[(IOTA0 - 64) & 127]));
			fVec8[0] = fTemp70;
			float fTemp71 = fTemp70 + fVec8[1];
			fVec9[0] = fTemp71;
			float fTemp72 = fTemp71 + fVec9[2];
			fVec10[0] = fTemp72;
			float fTemp73 = fTemp72 + fVec10[4];
			fVec11[0] = fTemp73;
			float fTemp74 = fTemp73 + fVec11[8];
			fVec12[IOTA0 & 31] = fTemp74;
			float fTemp75 = fTemp74 + fVec12[(IOTA0 - 16) & 31];
			fVec13[IOTA0 & 63] = fTemp75;
			float fTemp76 = fTemp75 + fVec13[(IOTA0 - 32) & 63];
			fVec14[IOTA0 & 127] = fTemp76;
			float fTemp77 = 1.0f - 0.0078125f * (fTemp76 + fVec14[(IOTA0 - 64) & 127]);
			float fTemp78 = std::max<float>(-fSlow2, std::min<float>(fSlow2, fVec0[(IOTA0 - 144) & 255] * fTemp77));
			fVec15[IOTA0 & 255] = fTemp78;
			float fTemp79 = fVec15[(IOTA0 - 15) & 255];
			float fTemp80 = fVec15[(IOTA0 - 16) & 255];
			float fTemp81 = fVec15[(IOTA0 - 31) & 255];
			float fTemp82 = fVec15[(IOTA0 - 29) & 255];
			float fTemp83 = fVec15[(IOTA0 - 27) & 255];
			float fTemp84 = fVec15[(IOTA0 - 25) & 255];
			float fTemp85 = fVec15[(IOTA0 - 23) & 255];
			float fTemp86 = fVec15[(IOTA0 - 21) & 255];
			float fTemp87 = fVec15[(IOTA0 - 19) & 255];
			float fTemp88 = fVec15[(IOTA0 - 17) & 255];
			float fTemp89 = fVec15[(IOTA0 - 14) & 255];
			float fTemp90 = fVec15[(IOTA0 - 12) & 255];
			float fTemp91 = fVec15[(IOTA0 - 10) & 255];
			float fTemp92 = fVec15[(IOTA0 - 8) & 255];
			float fTemp93 = fVec15[(IOTA0 - 6) & 255];
			float fTemp94 = fVec15[(IOTA0 - 4) & 255];
			float fTemp95 = fVec15[(IOTA0 - 2) & 255];
			float fTemp96 = fVec15[(IOTA0 - 30) & 255];
			float fTemp97 = fVec15[(IOTA0 - 28) & 255];
			float fTemp98 = fVec15[(IOTA0 - 26) & 255];
			float fTemp99 = fVec15[(IOTA0 - 24) & 255];
			float fTemp100 = fVec15[(IOTA0 - 22) & 255];
			float fTemp101 = fVec15[(IOTA0 - 20) & 255];
			float fTemp102 = fVec15[(IOTA0 - 18) & 255];
			float fTemp103 = fVec15[(IOTA0 - 1) & 255];
			float fTemp104 = fVec15[(IOTA0 - 3) & 255];
			float fTemp105 = fVec15[(IOTA0 - 5) & 255];
			float fTemp106 = fVec15[(IOTA0 - 7) & 255];
			float fTemp107 = fVec15[(IOTA0 - 9) & 255];
			float fTemp108 = fVec15[(IOTA0 - 11) & 255];
			float fTemp109 = fVec15[(IOTA0 - 13) & 255];
			float fTemp110 = std::max<float>(-fSlow2, std::min<float>(fSlow2, fVec1[(IOTA0 - 144) & 255] * fTemp77));
			fVec16[IOTA0 & 255] = fTemp110;
			float fTemp111 = fVec16[(IOTA0 - 15) & 255];
			float fTemp112 = fVec16[(IOTA0 - 16) & 255];
			float fTemp113 = fVec16[(IOTA0 - 31) & 255];
			float fTemp114 = fVec16[(IOTA0 - 29) & 255];
			float fTemp115 = fVec16[(IOTA0 - 27) & 255];
			float fTemp116 = fVec16[(IOTA0 - 25) & 255];
			float fTemp117 = fVec16[(IOTA0 - 23) & 255];
			float fTemp118 = fVec16[(IOTA0 - 21) & 255];
			float fTemp119 = fVec16[(IOTA0 - 19) & 255];
			float fTemp120 = fVec16[(IOTA0 - 17) & 255];
			float fTemp121 = fVec16[(IOTA0 - 14) & 255];
			float fTemp122 = fVec16[(IOTA0 - 12) & 255];
			float fTemp123 = fVec16[(IOTA0 - 10) & 255];
			float fTemp124 = fVec16[(IOTA0 - 8) & 255];
			float fTemp125 = fVec16[(IOTA0 - 6) & 255];
			float fTemp126 = fVec16[(IOTA0 - 4) & 255];
			float fTemp127 = fVec16[(IOTA0 - 2) & 255];
			float fTemp128 = fVec16[(IOTA0 - 30) & 255];
			float fTemp129 = fVec16[(IOTA0 - 28) & 255];
			float fTemp130 = fVec16[(IOTA0 - 26) & 255];
			float fTemp131 = fVec16[(IOTA0 - 24) & 255];
			float fTemp132 = fVec16[(IOTA0 - 22) & 255];
			float fTemp133 = fVec16[(IOTA0 - 20) & 255];
			float fTemp134 = fVec16[(IOTA0 - 18) & 255];
			float fTemp135 = fVec16[(IOTA0 - 1) & 255];
			float fTemp136 = fVec16[(IOTA0 - 3) & 255];
			float fTemp137 = fVec16[(IOTA0 - 5) & 255];
			float fTemp138 = fVec16[(IOTA0 - 7) & 255];
			float fTemp139 = fVec16[(IOTA0 - 9) & 255];
			float fTemp140 = fVec16[(IOTA0 - 11) & 255];
			float fTemp141 = fVec16[(IOTA0 - 13) & 255];
			fRec0[0] = std::max<float>(1.0f - fSlow1 / std::max<float>(fSlow1, std::max<float>(std::max<float>(std::max<float>(std::fabs(fTemp79), std::fabs(fTemp80)), std::max<float>(std::fabs(0.09441519f * fTemp109 + 0.043584947f * fTemp108 + 0.023639692f * fTemp107 + 0.0128541235f * fTemp106 + 0.006525907f * fTemp105 + 0.0029899369f * fTemp104 + 0.0014147608f * fTemp103 + 0.89973646f * fTemp79 + 0.29991215f * fTemp80 + 0.07724879f * fTemp102 + 0.038997058f * fTemp101 + 0.021888603f * fTemp100 + 0.012119602f * fTemp99 + 0.0062223766f * fTemp98 + 0.0028726843f * fTemp97 + 0.0013668028f * fTemp96 - (0.0011827738f * fTemp78 + 0.001995664f * fTemp95 + 0.0044707493f * fTemp94 + 0.009268237f * fTemp93 + 0.017517908f * fTemp92 + 0.03189086f * fTemp91 + 0.061675683f * fTemp90 + 0.17656787f * fTemp89 + 0.1261199f * fTemp88 + 0.05345226f * fTemp87 + 0.029117743f * fTemp86 + 0.01638772f * fTemp85 + 0.008792942f * fTemp84 + 0.004280505f * fTemp83 + 0.0019230944f * fTemp82 + 0.0011452254f * fTemp81)), std::max<float>(std::fabs(0.0019660336f * (fTemp103 + fTemp96) + 0.004143326f * (fTemp104 + fTemp97) + 0.009008168f * (fTemp105 + fTemp98) + 0.017641623f * (fTemp106 + fTemp99) + 0.058206834f * (fTemp108 + fTemp101) + 0.12015598f * (fTemp109 + fTemp102) + 0.6361307f * (fTemp79 + fTemp80) + 0.03214175f * (fTemp107 + fTemp100) - (0.002769686f * (fTemp95 + fTemp82) + 0.006184378f * (fTemp94 + fTemp83) + 0.023945283f * (fTemp92 + fTemp85) + 0.012760753f * (fTemp93 + fTemp84) + 0.04304512f * (fTemp91 + fTemp86) + 0.20806137f * (fTemp89 + fTemp88) + 0.08098234f * (fTemp90 + fTemp87) + 0.0016455112f * (fTemp78 + fTemp81))), std::fabs(0.07724879f * fTemp109 + 0.038997058f * fTemp108 + 0.021888603f * fTemp107 + 0.012119602f * fTemp106 + 0.0062223766f * fTemp105 + 0.0028726843f * fTemp104 + 0.0013668028f * fTemp103 + 0.29991215f * fTemp79 + 0.89973646f * fTemp80 + 0.09441519f * fTemp102 + 0.043584947f * fTemp101 + 0.023639692f * fTemp100 + 0.0128541235f * fTemp99 + 0.006525907f * fTemp98 + 0.0029899369f * fTemp97 + 0.0014147608f * fTemp96 - (0.0011452254f * fTemp78 + 0.0019230944f * fTemp95 + 0.004280505f * fTemp94 + 0.008792942f * fTemp93 + 0.01638772f * fTemp92 + 0.029117743f * fTemp91 + 0.05345226f * fTemp90 + 0.1261199f * fTemp89 + 0.17656787f * fTemp88 + 0.061675683f * fTemp87 + 0.03189086f * fTemp86 + 0.017517908f * fTemp85 + 0.009268237f * fTemp84 + 0.0044707493f * fTemp83 + 0.001995664f * fTemp82 + 0.0011827738f * fTemp81))))), std::max<float>(std::max<float>(std::fabs(fTemp111), std::fabs(fTemp112)), std::max<float>(std::fabs(0.09441519f * fTemp141 + 0.043584947f * fTemp140 + 0.023639692f * fTemp139 + 0.0128541235f * fTemp138 + 0.006525907f * fTemp137 + 0.0029899369f * fTemp136 + 0.0014147608f * fTemp135 + 0.89973646f * fTemp111 + 0.29991215f * fTemp112 + 0.07724879f * fTemp134 + 0.038997058f * fTemp133 + 0.021888603f * fTemp132 + 0.012119602f * fTemp131 + 0.0062223766f * fTemp130 + 0.0028726843f * fTemp129 + 0.0013668028f * fTemp128 - (0.0011827738f * fTemp110 + 0.001995664f * fTemp127 + 0.0044707493f * fTemp126 + 0.009268237f * fTemp125 + 0.017517908f * fTemp124 + 0.03189086f * fTemp123 + 0.061675683f * fTemp122 + 0.17656787f * fTemp121 + 0.1261199f * fTemp120 + 0.05345226f * fTemp119 + 0.029117743f * fTemp118 + 0.01638772f * fTemp117 + 0.008792942f * fTemp116 + 0.004280505f * fTemp115 + 0.0019230944f * fTemp114 + 0.0011452254f * fTemp113)), std::max<float>(std::fabs(0.0019660336f * (fTemp135 + fTemp128) + 0.004143326f * (fTemp136 + fTemp129) + 0.009008168f * (fTemp137 + fTemp130) + 0.017641623f * (fTemp138 + fTemp131) + 0.03214175f * (fTemp139 + fTemp132) + 0.058206834f * (fTemp140 + fTemp133) + 0.6361307f * (fTemp111 + fTemp112) + 0.12015598f * (fTemp141 + fTemp134) - (0.002769686f * (fTemp127 + fTemp114) + 0.006184378f * (fTemp126 + fTemp115) + 0.012760753f * (fTemp125 + fTemp116) + 0.04304512f * (fTemp123 + fTemp118) + 0.08098234f * (fTemp122 + fTemp119) + 0.20806137f * (fTemp121 + fTemp120) + 0.023945283f * (fTemp124 + fTemp117) + 0.0016455112f * (fTemp110 + fTemp113))), std::fabs(0.07724879f * fTemp141 + 0.038997058f * fTemp140 + 0.021888603f * fTemp139 + 0.012119602f * fTemp138 + 0.0062223766f * fTemp137 + 0.0028726843f * fTemp136 + 0.0013668028f * fTemp135 + 0.29991215f * fTemp111 + 0.89973646f * fTemp112 + 0.09441519f * fTemp134 + 0.043584947f * fTemp133 + 0.023639692f * fTemp132 + 0.0128541235f * fTemp131 + 0.006525907f * fTemp130 + 0.0029899369f * fTemp129 + 0.0014147608f * fTemp128 - (0.0011452254f * fTemp110 + 0.0019230944f * fTemp127 + 0.004280505f * fTemp126 + 0.008792942f * fTemp125 + 0.01638772f * fTemp124 + 0.029117743f * fTemp123 + 0.05345226f * fTemp122 + 0.1261199f * fTemp121 + 0.17656787f * fTemp120 + 0.061675683f * fTemp119 + 0.03189086f * fTemp118 + 0.017517908f * fTemp117 + 0.009268237f * fTemp116 + 0.0044707493f * fTemp115 + 0.001995664f * fTemp114 + 0.0011827738f * fTemp113))))))), fConst0 * fRec0[1]);
			float fTemp142 = std::max<float>(fRec0[0], fRec0[1]);
			fVec17[0] = fTemp142;
			float fTemp143 = std::max<float>(fTemp142, fVec17[2]);
			fVec18[0] = fTemp143;
			float fTemp144 = std::max<float>(fTemp143, fVec18[4]);
			fVec19[0] = fTemp144;
			float fTemp145 = std::max<float>(fTemp144, fVec19[8]);
			fVec20[IOTA0 & 31] = fTemp145;
			float fTemp146 = std::max<float>(fTemp145, fVec20[(IOTA0 - 16) & 31]);
			fVec21[IOTA0 & 63] = fTemp146;
			float fTemp147 = std::max<float>(fTemp146, fVec21[(IOTA0 - 32) & 63]);
			fVec22[IOTA0 & 127] = fTemp147;
			float fTemp148 = std::max<float>(-3.4028235e+38f, std::max<float>(fTemp147, fVec22[(IOTA0 - 64) & 127]));
			fVec23[0] = fTemp148;
			float fTemp149 = fTemp148 + fVec23[1];
			fVec24[0] = fTemp149;
			float fTemp150 = fTemp149 + fVec24[2];
			fVec25[0] = fTemp150;
			float fTemp151 = fTemp150 + fVec25[4];
			fVec26[0] = fTemp151;
			float fTemp152 = fTemp151 + fVec26[8];
			fVec27[IOTA0 & 31] = fTemp152;
			float fTemp153 = fTemp152 + fVec27[(IOTA0 - 16) & 31];
			fVec28[IOTA0 & 63] = fTemp153;
			float fTemp154 = fTemp153 + fVec28[(IOTA0 - 32) & 63];
			fVec29[IOTA0 & 127] = fTemp154;
			float fTemp155 = 1.0f - 0.0078125f * (fTemp154 + fVec29[(IOTA0 - 64) & 127]);
			output0[i0] = FAUSTFLOAT(std::max<float>(-fSlow1, std::min<float>(fSlow1, fVec15[(IOTA0 - 144) & 255] * fTemp155)));
			output1[i0] = FAUSTFLOAT(std::max<float>(-fSlow1, std::min<float>(fSlow1, fTemp155 * fVec16[(IOTA0 - 144) & 255])));
			IOTA0 = IOTA0 + 1;
			fRec1[1] = fRec1[0];
			fVec2[2] = fVec2[1];
			fVec2[1] = fVec2[0];
			for (int j0 = 4; j0 > 0; j0 = j0 - 1) {
				fVec3[j0] = fVec3[j0 - 1];
			}
			for (int j1 = 8; j1 > 0; j1 = j1 - 1) {
				fVec4[j1] = fVec4[j1 - 1];
			}
			fVec8[1] = fVec8[0];
			fVec9[2] = fVec9[1];
			fVec9[1] = fVec9[0];
			for (int j2 = 4; j2 > 0; j2 = j2 - 1) {
				fVec10[j2] = fVec10[j2 - 1];
			}
			for (int j3 = 8; j3 > 0; j3 = j3 - 1) {
				fVec11[j3] = fVec11[j3 - 1];
			}
			fRec0[1] = fRec0[0];
			fVec17[2] = fVec17[1];
			fVec17[1] = fVec17[0];
			for (int j4 = 4; j4 > 0; j4 = j4 - 1) {
				fVec18[j4] = fVec18[j4 - 1];
			}
			for (int j5 = 8; j5 > 0; j5 = j5 - 1) {
				fVec19[j5] = fVec19[j5 - 1];
			}
			fVec23[1] = fVec23[0];
			fVec24[2] = fVec24[1];
			fVec24[1] = fVec24[0];
			for (int j6 = 4; j6 > 0; j6 = j6 - 1) {
				fVec25[j6] = fVec25[j6 - 1];
			}
			for (int j7 = 8; j7 > 0; j7 = j7 - 1) {
				fVec26[j7] = fVec26[j7 - 1];
			}
		}
	}

};

#endif
