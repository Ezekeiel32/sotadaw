/* ------------------------------------------------------------
name: "fx_reverb"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn FxReverb -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __FxReverb_H__
#define  __FxReverb_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS FxReverb
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

static float FxReverb_faustpower2_f(float value) {
	return value * value;
}

class FxReverb : public dsp {
	
 private:
	
	int fSampleRate;
	float fConst1;
	float fConst2;
	FAUSTFLOAT fHslider0;
	float fRec0[2];
	FAUSTFLOAT fHslider1;
	float fConst5;
	FAUSTFLOAT fHslider2;
	float fConst6;
	float fConst8;
	float fConst9;
	float fRec12[2];
	float fConst10;
	float fRec11[2];
	int IOTA0;
	float fVec0[16384];
	int iConst12;
	float fVec1[4096];
	int iConst13;
	float fVec2[2048];
	int iConst14;
	float fRec9[2];
	float fConst17;
	float fRec16[2];
	float fConst18;
	float fRec15[2];
	float fVec3[16384];
	int iConst20;
	float fVec4[2048];
	int iConst21;
	float fRec13[2];
	float fConst24;
	float fRec20[2];
	float fConst25;
	float fRec19[2];
	float fVec5[16384];
	int iConst27;
	float fVec6[4096];
	int iConst28;
	float fRec17[2];
	float fConst31;
	float fRec24[2];
	float fConst32;
	float fRec23[2];
	float fVec7[16384];
	int iConst34;
	float fVec8[2048];
	int iConst35;
	float fRec21[2];
	float fConst38;
	float fRec28[2];
	float fConst39;
	float fRec27[2];
	float fVec9[32768];
	int iConst41;
	float fVec10[4096];
	float fVec11[4096];
	int iConst42;
	float fRec25[2];
	float fConst45;
	float fRec32[2];
	float fConst46;
	float fRec31[2];
	float fVec12[16384];
	int iConst48;
	float fVec13[4096];
	int iConst49;
	float fRec29[2];
	float fConst52;
	float fRec36[2];
	float fConst53;
	float fRec35[2];
	float fVec14[32768];
	int iConst55;
	float fVec15[4096];
	int iConst56;
	float fRec33[2];
	float fConst59;
	float fRec40[2];
	float fConst60;
	float fRec39[2];
	float fVec16[32768];
	int iConst62;
	float fVec17[2048];
	int iConst63;
	float fRec37[2];
	float fRec1[3];
	float fRec2[3];
	float fRec3[3];
	float fRec4[3];
	float fRec5[3];
	float fRec6[3];
	float fRec7[3];
	float fRec8[3];
	
 public:
	FxReverb() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn FxReverb -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("delays.lib/name", "Faust Delay Library");
		m->declare("delays.lib/version", "1.1.0");
		m->declare("filename", "fx_reverb.dsp");
		m->declare("filters.lib/allpass_comb:author", "Julius O. Smith III");
		m->declare("filters.lib/allpass_comb:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/allpass_comb:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/tf1:author", "Julius O. Smith III");
		m->declare("filters.lib/tf1:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf1:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf1s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf1s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf1s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/version", "1.3.0");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "fx_reverb");
		m->declare("platform.lib/name", "Generic Platform Library");
		m->declare("platform.lib/version", "1.3.0");
		m->declare("reverbs.lib/name", "Faust Reverb Library");
		m->declare("reverbs.lib/version", "1.2.1");
		m->declare("routes.lib/hadamard:author", "Remy Muller, revised by Romain Michon");
		m->declare("routes.lib/name", "Faust Signal Routing Library");
		m->declare("routes.lib/version", "1.2.0");
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
		float fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = 44.1f / fConst0;
		fConst2 = 1.0f - fConst1;
		float fConst3 = std::floor(0.174713f * fConst0 + 0.5f);
		float fConst4 = fConst3 / fConst0;
		fConst5 = 11.512925f * fConst4;
		fConst6 = 6.2831855f / fConst0;
		float fConst7 = 1.0f / std::tan(628.31854f / fConst0);
		fConst8 = 1.0f - fConst7;
		fConst9 = 1.0f / (fConst7 + 1.0f);
		fConst10 = 6.9077554f * fConst4;
		float fConst11 = std::floor(0.022904f * fConst0 + 0.5f);
		iConst12 = int(std::min<float>(8192.0f, std::max<float>(0.0f, fConst3 - fConst11)));
		iConst13 = int(std::min<float>(8192.0f, std::max<float>(0.0f, 0.02f * fConst0)));
		iConst14 = int(std::min<float>(1024.0f, std::max<float>(0.0f, fConst11 + -1.0f)));
		float fConst15 = std::floor(0.153129f * fConst0 + 0.5f);
		float fConst16 = fConst15 / fConst0;
		fConst17 = 11.512925f * fConst16;
		fConst18 = 6.9077554f * fConst16;
		float fConst19 = std::floor(0.020346f * fConst0 + 0.5f);
		iConst20 = int(std::min<float>(8192.0f, std::max<float>(0.0f, fConst15 - fConst19)));
		iConst21 = int(std::min<float>(1024.0f, std::max<float>(0.0f, fConst19 + -1.0f)));
		float fConst22 = std::floor(0.127837f * fConst0 + 0.5f);
		float fConst23 = fConst22 / fConst0;
		fConst24 = 11.512925f * fConst23;
		fConst25 = 6.9077554f * fConst23;
		float fConst26 = std::floor(0.031604f * fConst0 + 0.5f);
		iConst27 = int(std::min<float>(8192.0f, std::max<float>(0.0f, fConst22 - fConst26)));
		iConst28 = int(std::min<float>(2048.0f, std::max<float>(0.0f, fConst26 + -1.0f)));
		float fConst29 = std::floor(0.125f * fConst0 + 0.5f);
		float fConst30 = fConst29 / fConst0;
		fConst31 = 11.512925f * fConst30;
		fConst32 = 6.9077554f * fConst30;
		float fConst33 = std::floor(0.013458f * fConst0 + 0.5f);
		iConst34 = int(std::min<float>(8192.0f, std::max<float>(0.0f, fConst29 - fConst33)));
		iConst35 = int(std::min<float>(1024.0f, std::max<float>(0.0f, fConst33 + -1.0f)));
		float fConst36 = std::floor(0.210389f * fConst0 + 0.5f);
		float fConst37 = fConst36 / fConst0;
		fConst38 = 11.512925f * fConst37;
		fConst39 = 6.9077554f * fConst37;
		float fConst40 = std::floor(0.024421f * fConst0 + 0.5f);
		iConst41 = int(std::min<float>(16384.0f, std::max<float>(0.0f, fConst36 - fConst40)));
		iConst42 = int(std::min<float>(2048.0f, std::max<float>(0.0f, fConst40 + -1.0f)));
		float fConst43 = std::floor(0.192303f * fConst0 + 0.5f);
		float fConst44 = fConst43 / fConst0;
		fConst45 = 11.512925f * fConst44;
		fConst46 = 6.9077554f * fConst44;
		float fConst47 = std::floor(0.029291f * fConst0 + 0.5f);
		iConst48 = int(std::min<float>(8192.0f, std::max<float>(0.0f, fConst43 - fConst47)));
		iConst49 = int(std::min<float>(2048.0f, std::max<float>(0.0f, fConst47 + -1.0f)));
		float fConst50 = std::floor(0.256891f * fConst0 + 0.5f);
		float fConst51 = fConst50 / fConst0;
		fConst52 = 11.512925f * fConst51;
		fConst53 = 6.9077554f * fConst51;
		float fConst54 = std::floor(0.027333f * fConst0 + 0.5f);
		iConst55 = int(std::min<float>(16384.0f, std::max<float>(0.0f, fConst50 - fConst54)));
		iConst56 = int(std::min<float>(2048.0f, std::max<float>(0.0f, fConst54 + -1.0f)));
		float fConst57 = std::floor(0.219991f * fConst0 + 0.5f);
		float fConst58 = fConst57 / fConst0;
		fConst59 = 11.512925f * fConst58;
		fConst60 = 6.9077554f * fConst58;
		float fConst61 = std::floor(0.019123f * fConst0 + 0.5f);
		iConst62 = int(std::min<float>(16384.0f, std::max<float>(0.0f, fConst57 - fConst61)));
		iConst63 = int(std::min<float>(1024.0f, std::max<float>(0.0f, fConst61 + -1.0f)));
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(0.25f);
		fHslider1 = FAUSTFLOAT(2.5f);
		fHslider2 = FAUSTFLOAT(5e+03f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			fRec0[l0] = 0.0f;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			fRec12[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			fRec11[l2] = 0.0f;
		}
		IOTA0 = 0;
		for (int l3 = 0; l3 < 16384; l3 = l3 + 1) {
			fVec0[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 4096; l4 = l4 + 1) {
			fVec1[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 2048; l5 = l5 + 1) {
			fVec2[l5] = 0.0f;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			fRec9[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			fRec16[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			fRec15[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 16384; l9 = l9 + 1) {
			fVec3[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 2048; l10 = l10 + 1) {
			fVec4[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 2; l11 = l11 + 1) {
			fRec13[l11] = 0.0f;
		}
		for (int l12 = 0; l12 < 2; l12 = l12 + 1) {
			fRec20[l12] = 0.0f;
		}
		for (int l13 = 0; l13 < 2; l13 = l13 + 1) {
			fRec19[l13] = 0.0f;
		}
		for (int l14 = 0; l14 < 16384; l14 = l14 + 1) {
			fVec5[l14] = 0.0f;
		}
		for (int l15 = 0; l15 < 4096; l15 = l15 + 1) {
			fVec6[l15] = 0.0f;
		}
		for (int l16 = 0; l16 < 2; l16 = l16 + 1) {
			fRec17[l16] = 0.0f;
		}
		for (int l17 = 0; l17 < 2; l17 = l17 + 1) {
			fRec24[l17] = 0.0f;
		}
		for (int l18 = 0; l18 < 2; l18 = l18 + 1) {
			fRec23[l18] = 0.0f;
		}
		for (int l19 = 0; l19 < 16384; l19 = l19 + 1) {
			fVec7[l19] = 0.0f;
		}
		for (int l20 = 0; l20 < 2048; l20 = l20 + 1) {
			fVec8[l20] = 0.0f;
		}
		for (int l21 = 0; l21 < 2; l21 = l21 + 1) {
			fRec21[l21] = 0.0f;
		}
		for (int l22 = 0; l22 < 2; l22 = l22 + 1) {
			fRec28[l22] = 0.0f;
		}
		for (int l23 = 0; l23 < 2; l23 = l23 + 1) {
			fRec27[l23] = 0.0f;
		}
		for (int l24 = 0; l24 < 32768; l24 = l24 + 1) {
			fVec9[l24] = 0.0f;
		}
		for (int l25 = 0; l25 < 4096; l25 = l25 + 1) {
			fVec10[l25] = 0.0f;
		}
		for (int l26 = 0; l26 < 4096; l26 = l26 + 1) {
			fVec11[l26] = 0.0f;
		}
		for (int l27 = 0; l27 < 2; l27 = l27 + 1) {
			fRec25[l27] = 0.0f;
		}
		for (int l28 = 0; l28 < 2; l28 = l28 + 1) {
			fRec32[l28] = 0.0f;
		}
		for (int l29 = 0; l29 < 2; l29 = l29 + 1) {
			fRec31[l29] = 0.0f;
		}
		for (int l30 = 0; l30 < 16384; l30 = l30 + 1) {
			fVec12[l30] = 0.0f;
		}
		for (int l31 = 0; l31 < 4096; l31 = l31 + 1) {
			fVec13[l31] = 0.0f;
		}
		for (int l32 = 0; l32 < 2; l32 = l32 + 1) {
			fRec29[l32] = 0.0f;
		}
		for (int l33 = 0; l33 < 2; l33 = l33 + 1) {
			fRec36[l33] = 0.0f;
		}
		for (int l34 = 0; l34 < 2; l34 = l34 + 1) {
			fRec35[l34] = 0.0f;
		}
		for (int l35 = 0; l35 < 32768; l35 = l35 + 1) {
			fVec14[l35] = 0.0f;
		}
		for (int l36 = 0; l36 < 4096; l36 = l36 + 1) {
			fVec15[l36] = 0.0f;
		}
		for (int l37 = 0; l37 < 2; l37 = l37 + 1) {
			fRec33[l37] = 0.0f;
		}
		for (int l38 = 0; l38 < 2; l38 = l38 + 1) {
			fRec40[l38] = 0.0f;
		}
		for (int l39 = 0; l39 < 2; l39 = l39 + 1) {
			fRec39[l39] = 0.0f;
		}
		for (int l40 = 0; l40 < 32768; l40 = l40 + 1) {
			fVec16[l40] = 0.0f;
		}
		for (int l41 = 0; l41 < 2048; l41 = l41 + 1) {
			fVec17[l41] = 0.0f;
		}
		for (int l42 = 0; l42 < 2; l42 = l42 + 1) {
			fRec37[l42] = 0.0f;
		}
		for (int l43 = 0; l43 < 3; l43 = l43 + 1) {
			fRec1[l43] = 0.0f;
		}
		for (int l44 = 0; l44 < 3; l44 = l44 + 1) {
			fRec2[l44] = 0.0f;
		}
		for (int l45 = 0; l45 < 3; l45 = l45 + 1) {
			fRec3[l45] = 0.0f;
		}
		for (int l46 = 0; l46 < 3; l46 = l46 + 1) {
			fRec4[l46] = 0.0f;
		}
		for (int l47 = 0; l47 < 3; l47 = l47 + 1) {
			fRec5[l47] = 0.0f;
		}
		for (int l48 = 0; l48 < 3; l48 = l48 + 1) {
			fRec6[l48] = 0.0f;
		}
		for (int l49 = 0; l49 < 3; l49 = l49 + 1) {
			fRec7[l49] = 0.0f;
		}
		for (int l50 = 0; l50 < 3; l50 = l50 + 1) {
			fRec8[l50] = 0.0f;
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
	
	virtual FxReverb* clone() {
		return new FxReverb();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("fx_reverb");
		ui_interface->addHorizontalSlider("damp", &fHslider2, FAUSTFLOAT(5e+03f), FAUSTFLOAT(1e+03f), FAUSTFLOAT(1.2e+04f), FAUSTFLOAT(1.0f));
		ui_interface->addHorizontalSlider("mix", &fHslider0, FAUSTFLOAT(0.25f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("size", &fHslider1, FAUSTFLOAT(2.5f), FAUSTFLOAT(0.5f), FAUSTFLOAT(8.0f), FAUSTFLOAT(0.1f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* input0 = inputs[0];
		FAUSTFLOAT* input1 = inputs[1];
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = fConst1 * float(fHslider0);
		float fSlow1 = float(fHslider1);
		float fSlow2 = std::exp(-(fConst5 / fSlow1));
		float fSlow3 = FxReverb_faustpower2_f(fSlow2);
		float fSlow4 = 1.0f - fSlow3;
		float fSlow5 = std::cos(fConst6 * float(fHslider2));
		float fSlow6 = 1.0f - fSlow5 * fSlow3;
		float fSlow7 = std::sqrt(std::max<float>(0.0f, FxReverb_faustpower2_f(fSlow6) / FxReverb_faustpower2_f(fSlow4) + -1.0f));
		float fSlow8 = fSlow6 / fSlow4;
		float fSlow9 = fSlow8 - fSlow7;
		float fSlow10 = std::exp(-(fConst10 / fSlow1)) / fSlow2 + -1.0f;
		float fSlow11 = fSlow2 * (fSlow7 + (1.0f - fSlow8));
		float fSlow12 = std::exp(-(fConst17 / fSlow1));
		float fSlow13 = FxReverb_faustpower2_f(fSlow12);
		float fSlow14 = 1.0f - fSlow13;
		float fSlow15 = 1.0f - fSlow13 * fSlow5;
		float fSlow16 = std::sqrt(std::max<float>(0.0f, FxReverb_faustpower2_f(fSlow15) / FxReverb_faustpower2_f(fSlow14) + -1.0f));
		float fSlow17 = fSlow15 / fSlow14;
		float fSlow18 = fSlow17 - fSlow16;
		float fSlow19 = std::exp(-(fConst18 / fSlow1)) / fSlow12 + -1.0f;
		float fSlow20 = fSlow12 * (fSlow16 + (1.0f - fSlow17));
		float fSlow21 = std::exp(-(fConst24 / fSlow1));
		float fSlow22 = FxReverb_faustpower2_f(fSlow21);
		float fSlow23 = 1.0f - fSlow22;
		float fSlow24 = 1.0f - fSlow5 * fSlow22;
		float fSlow25 = std::sqrt(std::max<float>(0.0f, FxReverb_faustpower2_f(fSlow24) / FxReverb_faustpower2_f(fSlow23) + -1.0f));
		float fSlow26 = fSlow24 / fSlow23;
		float fSlow27 = fSlow26 - fSlow25;
		float fSlow28 = std::exp(-(fConst25 / fSlow1)) / fSlow21 + -1.0f;
		float fSlow29 = fSlow21 * (fSlow25 + (1.0f - fSlow26));
		float fSlow30 = std::exp(-(fConst31 / fSlow1));
		float fSlow31 = FxReverb_faustpower2_f(fSlow30);
		float fSlow32 = 1.0f - fSlow31;
		float fSlow33 = 1.0f - fSlow5 * fSlow31;
		float fSlow34 = std::sqrt(std::max<float>(0.0f, FxReverb_faustpower2_f(fSlow33) / FxReverb_faustpower2_f(fSlow32) + -1.0f));
		float fSlow35 = fSlow33 / fSlow32;
		float fSlow36 = fSlow35 - fSlow34;
		float fSlow37 = std::exp(-(fConst32 / fSlow1)) / fSlow30 + -1.0f;
		float fSlow38 = fSlow30 * (fSlow34 + (1.0f - fSlow35));
		float fSlow39 = std::exp(-(fConst38 / fSlow1));
		float fSlow40 = FxReverb_faustpower2_f(fSlow39);
		float fSlow41 = 1.0f - fSlow40;
		float fSlow42 = 1.0f - fSlow5 * fSlow40;
		float fSlow43 = std::sqrt(std::max<float>(0.0f, FxReverb_faustpower2_f(fSlow42) / FxReverb_faustpower2_f(fSlow41) + -1.0f));
		float fSlow44 = fSlow42 / fSlow41;
		float fSlow45 = fSlow44 - fSlow43;
		float fSlow46 = std::exp(-(fConst39 / fSlow1)) / fSlow39 + -1.0f;
		float fSlow47 = fSlow39 * (fSlow43 + (1.0f - fSlow44));
		float fSlow48 = std::exp(-(fConst45 / fSlow1));
		float fSlow49 = FxReverb_faustpower2_f(fSlow48);
		float fSlow50 = 1.0f - fSlow49;
		float fSlow51 = 1.0f - fSlow5 * fSlow49;
		float fSlow52 = std::sqrt(std::max<float>(0.0f, FxReverb_faustpower2_f(fSlow51) / FxReverb_faustpower2_f(fSlow50) + -1.0f));
		float fSlow53 = fSlow51 / fSlow50;
		float fSlow54 = fSlow53 - fSlow52;
		float fSlow55 = std::exp(-(fConst46 / fSlow1)) / fSlow48 + -1.0f;
		float fSlow56 = fSlow48 * (fSlow52 + (1.0f - fSlow53));
		float fSlow57 = std::exp(-(fConst52 / fSlow1));
		float fSlow58 = FxReverb_faustpower2_f(fSlow57);
		float fSlow59 = 1.0f - fSlow58;
		float fSlow60 = 1.0f - fSlow5 * fSlow58;
		float fSlow61 = std::sqrt(std::max<float>(0.0f, FxReverb_faustpower2_f(fSlow60) / FxReverb_faustpower2_f(fSlow59) + -1.0f));
		float fSlow62 = fSlow60 / fSlow59;
		float fSlow63 = fSlow62 - fSlow61;
		float fSlow64 = std::exp(-(fConst53 / fSlow1)) / fSlow57 + -1.0f;
		float fSlow65 = fSlow57 * (fSlow61 + (1.0f - fSlow62));
		float fSlow66 = std::exp(-(fConst59 / fSlow1));
		float fSlow67 = FxReverb_faustpower2_f(fSlow66);
		float fSlow68 = 1.0f - fSlow67;
		float fSlow69 = 1.0f - fSlow5 * fSlow67;
		float fSlow70 = std::sqrt(std::max<float>(0.0f, FxReverb_faustpower2_f(fSlow69) / FxReverb_faustpower2_f(fSlow68) + -1.0f));
		float fSlow71 = fSlow69 / fSlow68;
		float fSlow72 = fSlow71 - fSlow70;
		float fSlow73 = std::exp(-(fConst60 / fSlow1)) / fSlow66 + -1.0f;
		float fSlow74 = fSlow66 * (fSlow70 + (1.0f - fSlow71));
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			fRec0[0] = fSlow0 + fConst2 * fRec0[1];
			fRec12[0] = -(fConst9 * (fConst8 * fRec12[1] - (fRec5[1] + fRec5[2])));
			fRec11[0] = fSlow11 * (fRec5[1] + fSlow10 * fRec12[0]) + fSlow9 * fRec11[1];
			fVec0[IOTA0 & 16383] = 0.35355338f * fRec11[0] + 1e-20f;
			float fTemp0 = float(input0[i0]);
			fVec1[IOTA0 & 4095] = fTemp0;
			float fTemp1 = 0.3f * fVec1[(IOTA0 - iConst13) & 4095];
			float fTemp2 = fTemp1 + fVec0[(IOTA0 - iConst12) & 16383] - 0.6f * fRec9[1];
			fVec2[IOTA0 & 2047] = fTemp2;
			fRec9[0] = fVec2[(IOTA0 - iConst14) & 2047];
			float fRec10 = 0.6f * fTemp2;
			fRec16[0] = -(fConst9 * (fConst8 * fRec16[1] - (fRec1[1] + fRec1[2])));
			fRec15[0] = fSlow20 * (fRec1[1] + fSlow19 * fRec16[0]) + fSlow18 * fRec15[1];
			fVec3[IOTA0 & 16383] = 0.35355338f * fRec15[0] + 1e-20f;
			float fTemp3 = fVec3[(IOTA0 - iConst20) & 16383] + fTemp1 - 0.6f * fRec13[1];
			fVec4[IOTA0 & 2047] = fTemp3;
			fRec13[0] = fVec4[(IOTA0 - iConst21) & 2047];
			float fRec14 = 0.6f * fTemp3;
			float fTemp4 = fRec14 + fRec10;
			fRec20[0] = -(fConst9 * (fConst8 * fRec20[1] - (fRec3[1] + fRec3[2])));
			fRec19[0] = fSlow29 * (fRec3[1] + fSlow28 * fRec20[0]) + fSlow27 * fRec19[1];
			fVec5[IOTA0 & 16383] = 0.35355338f * fRec19[0] + 1e-20f;
			float fTemp5 = fVec5[(IOTA0 - iConst27) & 16383] - (fTemp1 + 0.6f * fRec17[1]);
			fVec6[IOTA0 & 4095] = fTemp5;
			fRec17[0] = fVec6[(IOTA0 - iConst28) & 4095];
			float fRec18 = 0.6f * fTemp5;
			fRec24[0] = -(fConst9 * (fConst8 * fRec24[1] - (fRec7[1] + fRec7[2])));
			fRec23[0] = fSlow38 * (fRec7[1] + fSlow37 * fRec24[0]) + fSlow36 * fRec23[1];
			fVec7[IOTA0 & 16383] = 0.35355338f * fRec23[0] + 1e-20f;
			float fTemp6 = fVec7[(IOTA0 - iConst34) & 16383] - (fTemp1 + 0.6f * fRec21[1]);
			fVec8[IOTA0 & 2047] = fTemp6;
			fRec21[0] = fVec8[(IOTA0 - iConst35) & 2047];
			float fRec22 = 0.6f * fTemp6;
			float fTemp7 = fRec22 + fRec18 + fTemp4;
			fRec28[0] = -(fConst9 * (fConst8 * fRec28[1] - (fRec2[1] + fRec2[2])));
			fRec27[0] = fSlow47 * (fRec2[1] + fSlow46 * fRec28[0]) + fSlow45 * fRec27[1];
			fVec9[IOTA0 & 32767] = 0.35355338f * fRec27[0] + 1e-20f;
			float fTemp8 = float(input1[i0]);
			fVec10[IOTA0 & 4095] = fTemp8;
			float fTemp9 = 0.3f * fVec10[(IOTA0 - iConst13) & 4095];
			float fTemp10 = fTemp9 + 0.6f * fRec25[1] + fVec9[(IOTA0 - iConst41) & 32767];
			fVec11[IOTA0 & 4095] = fTemp10;
			fRec25[0] = fVec11[(IOTA0 - iConst42) & 4095];
			float fRec26 = -(0.6f * fTemp10);
			fRec32[0] = -(fConst9 * (fConst8 * fRec32[1] - (fRec6[1] + fRec6[2])));
			fRec31[0] = fSlow56 * (fRec6[1] + fSlow55 * fRec32[0]) + fSlow54 * fRec31[1];
			fVec12[IOTA0 & 16383] = 0.35355338f * fRec31[0] + 1e-20f;
			float fTemp11 = fVec12[(IOTA0 - iConst48) & 16383] + fTemp9 + 0.6f * fRec29[1];
			fVec13[IOTA0 & 4095] = fTemp11;
			fRec29[0] = fVec13[(IOTA0 - iConst49) & 4095];
			float fRec30 = -(0.6f * fTemp11);
			fRec36[0] = -(fConst9 * (fConst8 * fRec36[1] - (fRec4[1] + fRec4[2])));
			fRec35[0] = fSlow65 * (fRec4[1] + fSlow64 * fRec36[0]) + fSlow63 * fRec35[1];
			fVec14[IOTA0 & 32767] = 0.35355338f * fRec35[0] + 1e-20f;
			float fTemp12 = 0.6f * fRec33[1] + fVec14[(IOTA0 - iConst55) & 32767];
			fVec15[IOTA0 & 4095] = fTemp12 - fTemp9;
			fRec33[0] = fVec15[(IOTA0 - iConst56) & 4095];
			float fRec34 = 0.6f * (fTemp9 - fTemp12);
			fRec40[0] = -(fConst9 * (fConst8 * fRec40[1] - (fRec8[1] + fRec8[2])));
			fRec39[0] = fSlow74 * (fRec8[1] + fSlow73 * fRec40[0]) + fSlow72 * fRec39[1];
			fVec16[IOTA0 & 32767] = 0.35355338f * fRec39[0] + 1e-20f;
			float fTemp13 = 0.6f * fRec37[1] + fVec16[(IOTA0 - iConst62) & 32767];
			fVec17[IOTA0 & 2047] = fTemp13 - fTemp9;
			fRec37[0] = fVec17[(IOTA0 - iConst63) & 2047];
			float fRec38 = 0.6f * (fTemp9 - fTemp13);
			fRec1[0] = fRec37[1] + fRec33[1] + fRec29[1] + fRec25[1] + fRec21[1] + fRec17[1] + fRec9[1] + fRec13[1] + fRec38 + fRec34 + fRec30 + fRec26 + fTemp7;
			fRec2[0] = fRec21[1] + fRec17[1] + fRec9[1] + fRec13[1] + fTemp7 - (fRec37[1] + fRec33[1] + fRec29[1] + fRec25[1] + fRec38 + fRec34 + fRec26 + fRec30);
			float fTemp14 = fRec18 + fRec22;
			fRec3[0] = fRec29[1] + fRec25[1] + fRec9[1] + fRec13[1] + fRec30 + fRec26 + fTemp4 - (fRec37[1] + fRec33[1] + fRec21[1] + fRec17[1] + fRec38 + fRec34 + fTemp14);
			fRec4[0] = fRec37[1] + fRec33[1] + fRec9[1] + fRec13[1] + fRec38 + fRec34 + fTemp4 - (fRec29[1] + fRec25[1] + fRec21[1] + fRec17[1] + fRec30 + fRec26 + fTemp14);
			float fTemp15 = fRec10 + fRec22;
			float fTemp16 = fRec14 + fRec18;
			fRec5[0] = fRec33[1] + fRec25[1] + fRec17[1] + fRec13[1] + fRec34 + fRec26 + fTemp16 - (fRec37[1] + fRec29[1] + fRec21[1] + fRec9[1] + fRec38 + fRec30 + fTemp15);
			fRec6[0] = fRec37[1] + fRec29[1] + fRec17[1] + fRec13[1] + fRec38 + fRec30 + fTemp16 - (fRec33[1] + fRec25[1] + fRec21[1] + fRec9[1] + fRec34 + fRec26 + fTemp15);
			float fTemp17 = fRec10 + fRec18;
			float fTemp18 = fRec14 + fRec22;
			fRec7[0] = fRec37[1] + fRec25[1] + fRec21[1] + fRec13[1] + fRec38 + fRec26 + fTemp18 - (fRec33[1] + fRec29[1] + fRec17[1] + fRec9[1] + fRec34 + fRec30 + fTemp17);
			fRec8[0] = fRec33[1] + fRec29[1] + fRec21[1] + fRec13[1] + fRec34 + fRec30 + fTemp18 - (fRec37[1] + fRec25[1] + fRec17[1] + fRec9[1] + fRec38 + fRec26 + fTemp17);
			float fTemp19 = 1.0f - fRec0[0];
			output0[i0] = FAUSTFLOAT(fTemp0 * fTemp19 + 0.37f * (fRec2[0] + fRec3[0]) * fRec0[0]);
			output1[i0] = FAUSTFLOAT(fTemp8 * fTemp19 + 0.37f * fRec0[0] * (fRec2[0] - fRec3[0]));
			fRec0[1] = fRec0[0];
			fRec12[1] = fRec12[0];
			fRec11[1] = fRec11[0];
			IOTA0 = IOTA0 + 1;
			fRec9[1] = fRec9[0];
			fRec16[1] = fRec16[0];
			fRec15[1] = fRec15[0];
			fRec13[1] = fRec13[0];
			fRec20[1] = fRec20[0];
			fRec19[1] = fRec19[0];
			fRec17[1] = fRec17[0];
			fRec24[1] = fRec24[0];
			fRec23[1] = fRec23[0];
			fRec21[1] = fRec21[0];
			fRec28[1] = fRec28[0];
			fRec27[1] = fRec27[0];
			fRec25[1] = fRec25[0];
			fRec32[1] = fRec32[0];
			fRec31[1] = fRec31[0];
			fRec29[1] = fRec29[0];
			fRec36[1] = fRec36[0];
			fRec35[1] = fRec35[0];
			fRec33[1] = fRec33[0];
			fRec40[1] = fRec40[0];
			fRec39[1] = fRec39[0];
			fRec37[1] = fRec37[0];
			fRec1[2] = fRec1[1];
			fRec1[1] = fRec1[0];
			fRec2[2] = fRec2[1];
			fRec2[1] = fRec2[0];
			fRec3[2] = fRec3[1];
			fRec3[1] = fRec3[0];
			fRec4[2] = fRec4[1];
			fRec4[1] = fRec4[0];
			fRec5[2] = fRec5[1];
			fRec5[1] = fRec5[0];
			fRec6[2] = fRec6[1];
			fRec6[1] = fRec6[0];
			fRec7[2] = fRec7[1];
			fRec7[1] = fRec7[0];
			fRec8[2] = fRec8[1];
			fRec8[1] = fRec8[0];
		}
	}

};

#endif
