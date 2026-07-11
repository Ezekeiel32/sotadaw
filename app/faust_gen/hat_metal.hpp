/* ------------------------------------------------------------
name: "hat_metal"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn HatMetal -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __HatMetal_H__
#define  __HatMetal_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS HatMetal
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

static float HatMetal_faustpower2_f(float value) {
	return value * value;
}

class HatMetal : public dsp {
	
 private:
	
	FAUSTFLOAT fButton0;
	float fVec0[2];
	int iVec1[2];
	int iRec0[2];
	int fSampleRate;
	float fConst0;
	float fConst1;
	float fConst2;
	FAUSTFLOAT fHslider0;
	FAUSTFLOAT fHslider1;
	float fConst3;
	FAUSTFLOAT fHslider2;
	float fConst4;
	float fRec4[2];
	float fVec2[2];
	int IOTA0;
	float fVec3[128];
	int iConst6;
	int iConst7;
	float fConst9;
	float fConst10;
	float fConst11;
	float fRec5[2];
	float fVec4[2];
	float fVec5[256];
	int iConst13;
	int iConst14;
	float fConst16;
	float fConst17;
	float fConst18;
	float fRec6[2];
	float fVec6[2];
	float fVec7[256];
	int iConst20;
	int iConst21;
	float fConst23;
	float fConst24;
	float fConst25;
	float fRec7[2];
	float fVec8[2];
	float fVec9[256];
	int iConst27;
	int iConst28;
	float fConst30;
	float fConst31;
	float fConst32;
	float fRec8[2];
	float fVec10[2];
	float fVec11[256];
	int iConst34;
	int iConst35;
	float fConst37;
	float fConst38;
	float fConst39;
	float fRec9[2];
	float fVec12[2];
	float fVec13[512];
	int iConst41;
	int iConst42;
	float fConst44;
	float fConst45;
	float fConst46;
	float fRec3[3];
	float fRec2[3];
	float fRec1[3];
	FAUSTFLOAT fHslider3;
	
 public:
	HatMetal() {}

	void metadata(Meta* m) { 
		m->declare("compile_options", "-lang cpp -ct 1 -cn HatMetal -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "hat_metal.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/highpass:author", "Julius O. Smith III");
		m->declare("filters.lib/highpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/resonbp:author", "Julius O. Smith III");
		m->declare("filters.lib/resonbp:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/resonbp:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/version", "1.3.0");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "hat_metal");
		m->declare("oscillators.lib/lf_sawpos:author", "Bart Brouns, revised by Stéphane Letz");
		m->declare("oscillators.lib/lf_sawpos:licence", "STK-4.3");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
		m->declare("oscillators.lib/sawN:author", "Julius O. Smith III");
		m->declare("oscillators.lib/sawN:license", "STK-4.3");
		m->declare("oscillators.lib/version", "1.5.0");
		m->declare("platform.lib/name", "Generic Platform Library");
		m->declare("platform.lib/version", "1.3.0");
	}

	virtual int getNumInputs() {
		return 0;
	}
	virtual int getNumOutputs() {
		return 2;
	}
	
	static void classInit(int sample_rate) {
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = std::max<float>(1.0f, 0.0005f * fConst0);
		fConst2 = 1.0f / fConst1;
		fConst3 = 3.1415927f / fConst0;
		fConst4 = 845.0f / fConst0;
		float fConst5 = std::max<float>(0.0f, std::min<float>(2047.0f, 0.000591716f * fConst0));
		iConst6 = int(fConst5);
		iConst7 = iConst6 + 1;
		float fConst8 = std::floor(fConst5);
		fConst9 = fConst5 - fConst8;
		fConst10 = fConst8 + (1.0f - fConst5);
		fConst11 = 587.0f / fConst0;
		float fConst12 = std::max<float>(0.0f, std::min<float>(2047.0f, 0.00085178873f * fConst0));
		iConst13 = int(fConst12);
		iConst14 = iConst13 + 1;
		float fConst15 = std::floor(fConst12);
		fConst16 = fConst12 - fConst15;
		fConst17 = fConst15 + (1.0f - fConst12);
		fConst18 = 474.0f / fConst0;
		float fConst19 = std::max<float>(0.0f, std::min<float>(2047.0f, 0.0010548523f * fConst0));
		iConst20 = int(fConst19);
		iConst21 = iConst20 + 1;
		float fConst22 = std::floor(fConst19);
		fConst23 = fConst19 - fConst22;
		fConst24 = fConst22 + (1.0f - fConst19);
		fConst25 = 421.0f / fConst0;
		float fConst26 = std::max<float>(0.0f, std::min<float>(2047.0f, 0.0011876485f * fConst0));
		iConst27 = int(fConst26);
		iConst28 = iConst27 + 1;
		float fConst29 = std::floor(fConst26);
		fConst30 = fConst26 - fConst29;
		fConst31 = fConst29 + (1.0f - fConst26);
		fConst32 = 4e+02f / fConst0;
		float fConst33 = std::max<float>(0.0f, std::min<float>(2047.0f, 0.00125f * fConst0));
		iConst34 = int(fConst33);
		iConst35 = iConst34 + 1;
		float fConst36 = std::floor(fConst33);
		fConst37 = fConst33 - fConst36;
		fConst38 = fConst36 + (1.0f - fConst33);
		fConst39 = 263.0f / fConst0;
		float fConst40 = std::max<float>(0.0f, std::min<float>(2047.0f, 0.0019011407f * fConst0));
		iConst41 = int(fConst40);
		iConst42 = iConst41 + 1;
		float fConst43 = std::floor(fConst40);
		fConst44 = fConst40 - fConst43;
		fConst45 = fConst43 + (1.0f - fConst40);
		fConst46 = 0.16666667f * fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(0.045f);
		fHslider1 = FAUSTFLOAT(1.05e+04f);
		fHslider2 = FAUSTFLOAT(7.5e+03f);
		fHslider3 = FAUSTFLOAT(0.6f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			fVec0[l0] = 0.0f;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			iVec1[l1] = 0;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec0[l2] = 0;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			fRec4[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			fVec2[l4] = 0.0f;
		}
		IOTA0 = 0;
		for (int l5 = 0; l5 < 128; l5 = l5 + 1) {
			fVec3[l5] = 0.0f;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			fRec5[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			fVec4[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 256; l8 = l8 + 1) {
			fVec5[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			fRec6[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 2; l10 = l10 + 1) {
			fVec6[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 256; l11 = l11 + 1) {
			fVec7[l11] = 0.0f;
		}
		for (int l12 = 0; l12 < 2; l12 = l12 + 1) {
			fRec7[l12] = 0.0f;
		}
		for (int l13 = 0; l13 < 2; l13 = l13 + 1) {
			fVec8[l13] = 0.0f;
		}
		for (int l14 = 0; l14 < 256; l14 = l14 + 1) {
			fVec9[l14] = 0.0f;
		}
		for (int l15 = 0; l15 < 2; l15 = l15 + 1) {
			fRec8[l15] = 0.0f;
		}
		for (int l16 = 0; l16 < 2; l16 = l16 + 1) {
			fVec10[l16] = 0.0f;
		}
		for (int l17 = 0; l17 < 256; l17 = l17 + 1) {
			fVec11[l17] = 0.0f;
		}
		for (int l18 = 0; l18 < 2; l18 = l18 + 1) {
			fRec9[l18] = 0.0f;
		}
		for (int l19 = 0; l19 < 2; l19 = l19 + 1) {
			fVec12[l19] = 0.0f;
		}
		for (int l20 = 0; l20 < 512; l20 = l20 + 1) {
			fVec13[l20] = 0.0f;
		}
		for (int l21 = 0; l21 < 3; l21 = l21 + 1) {
			fRec3[l21] = 0.0f;
		}
		for (int l22 = 0; l22 < 3; l22 = l22 + 1) {
			fRec2[l22] = 0.0f;
		}
		for (int l23 = 0; l23 < 3; l23 = l23 + 1) {
			fRec1[l23] = 0.0f;
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
	
	virtual HatMetal* clone() {
		return new HatMetal();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("hat_metal");
		ui_interface->addHorizontalSlider("decay", &fHslider0, FAUSTFLOAT(0.045f), FAUSTFLOAT(0.01f), FAUSTFLOAT(0.4f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider3, FAUSTFLOAT(0.6f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("sizzle", &fHslider2, FAUSTFLOAT(7.5e+03f), FAUSTFLOAT(5e+03f), FAUSTFLOAT(1e+04f), FAUSTFLOAT(1.0f));
		ui_interface->addHorizontalSlider("tone", &fHslider1, FAUSTFLOAT(1.05e+04f), FAUSTFLOAT(6e+03f), FAUSTFLOAT(1.4e+04f), FAUSTFLOAT(1.0f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fButton0);
		float fSlow1 = 1.0f / std::max<float>(1.0f, fConst0 * float(fHslider0));
		float fSlow2 = std::tan(fConst3 * float(fHslider1));
		float fSlow3 = 2.0f * (1.0f - 1.0f / HatMetal_faustpower2_f(fSlow2));
		float fSlow4 = 1.0f / fSlow2;
		float fSlow5 = (fSlow4 + -0.4f) / fSlow2 + 1.0f;
		float fSlow6 = (fSlow4 + 0.4f) / fSlow2 + 1.0f;
		float fSlow7 = 1.0f / fSlow6;
		float fSlow8 = std::tan(fConst3 * float(fHslider2));
		float fSlow9 = HatMetal_faustpower2_f(fSlow8);
		float fSlow10 = 2.0f * (1.0f - 1.0f / fSlow9);
		float fSlow11 = 1.0f / fSlow8;
		float fSlow12 = (fSlow11 + -0.76536685f) / fSlow8 + 1.0f;
		float fSlow13 = (fSlow11 + 0.76536685f) / fSlow8 + 1.0f;
		float fSlow14 = 1.0f / fSlow13;
		float fSlow15 = (fSlow11 + -1.847759f) / fSlow8 + 1.0f;
		float fSlow16 = (fSlow11 + 1.847759f) / fSlow8 + 1.0f;
		float fSlow17 = 1.0f / fSlow16;
		float fSlow18 = 1.0f / (fSlow9 * fSlow16);
		float fSlow19 = 1.0f / (fSlow9 * fSlow13);
		float fSlow20 = 1.4f * (float(fHslider3) / (fSlow2 * fSlow6));
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			fVec0[0] = fSlow0;
			iVec1[0] = 1;
			iRec0[0] = (iRec0[1] + (iRec0[1] > 0)) * (fSlow0 <= fVec0[1]) + (fSlow0 > fVec0[1]);
			float fTemp0 = float(iRec0[0]);
			int iTemp1 = 1 - iVec1[1];
			float fTemp2 = ((iTemp1) ? 0.0f : fConst4 + fRec4[1]);
			fRec4[0] = fTemp2 - std::floor(fTemp2);
			float fTemp3 = HatMetal_faustpower2_f(2.0f * fRec4[0] + -1.0f);
			fVec2[0] = fTemp3;
			float fTemp4 = float(iVec1[1]);
			float fTemp5 = fTemp4 * (fTemp3 - fVec2[1]);
			fVec3[IOTA0 & 127] = fTemp5;
			float fTemp6 = ((iTemp1) ? 0.0f : fConst11 + fRec5[1]);
			fRec5[0] = fTemp6 - std::floor(fTemp6);
			float fTemp7 = HatMetal_faustpower2_f(2.0f * fRec5[0] + -1.0f);
			fVec4[0] = fTemp7;
			float fTemp8 = fTemp4 * (fTemp7 - fVec4[1]);
			fVec5[IOTA0 & 255] = fTemp8;
			float fTemp9 = ((iTemp1) ? 0.0f : fConst18 + fRec6[1]);
			fRec6[0] = fTemp9 - std::floor(fTemp9);
			float fTemp10 = HatMetal_faustpower2_f(2.0f * fRec6[0] + -1.0f);
			fVec6[0] = fTemp10;
			float fTemp11 = fTemp4 * (fTemp10 - fVec6[1]);
			fVec7[IOTA0 & 255] = fTemp11;
			float fTemp12 = ((iTemp1) ? 0.0f : fConst25 + fRec7[1]);
			fRec7[0] = fTemp12 - std::floor(fTemp12);
			float fTemp13 = HatMetal_faustpower2_f(2.0f * fRec7[0] + -1.0f);
			fVec8[0] = fTemp13;
			float fTemp14 = fTemp4 * (fTemp13 - fVec8[1]);
			fVec9[IOTA0 & 255] = fTemp14;
			float fTemp15 = ((iTemp1) ? 0.0f : fConst32 + fRec8[1]);
			fRec8[0] = fTemp15 - std::floor(fTemp15);
			float fTemp16 = HatMetal_faustpower2_f(2.0f * fRec8[0] + -1.0f);
			fVec10[0] = fTemp16;
			float fTemp17 = fTemp4 * (fTemp16 - fVec10[1]);
			fVec11[IOTA0 & 255] = fTemp17;
			float fTemp18 = ((iTemp1) ? 0.0f : fConst39 + fRec9[1]);
			fRec9[0] = fTemp18 - std::floor(fTemp18);
			float fTemp19 = HatMetal_faustpower2_f(2.0f * fRec9[0] + -1.0f);
			fVec12[0] = fTemp19;
			float fTemp20 = fTemp4 * (fTemp19 - fVec12[1]);
			fVec13[IOTA0 & 511] = fTemp20;
			fRec3[0] = fConst46 * (0.00095057033f * (fTemp20 - fConst45 * fVec13[(IOTA0 - iConst41) & 511] - fConst44 * fVec13[(IOTA0 - iConst42) & 511]) + 0.000625f * (fTemp17 - fConst38 * fVec11[(IOTA0 - iConst34) & 255] - fConst37 * fVec11[(IOTA0 - iConst35) & 255]) + 0.00059382425f * (fTemp14 - fConst31 * fVec9[(IOTA0 - iConst27) & 255] - fConst30 * fVec9[(IOTA0 - iConst28) & 255]) + 0.00052742613f * (fTemp11 - fConst24 * fVec7[(IOTA0 - iConst20) & 255] - fConst23 * fVec7[(IOTA0 - iConst21) & 255]) + 0.00042589437f * (fTemp8 - fConst17 * fVec5[(IOTA0 - iConst13) & 255] - fConst16 * fVec5[(IOTA0 - iConst14) & 255]) + 0.000295858f * (fTemp5 - fConst10 * fVec3[(IOTA0 - iConst6) & 127] - fConst9 * fVec3[(IOTA0 - iConst7) & 127])) - fSlow17 * (fSlow15 * fRec3[2] + fSlow10 * fRec3[1]);
			fRec2[0] = fSlow18 * (fRec3[2] + (fRec3[0] - 2.0f * fRec3[1])) - fSlow14 * (fSlow12 * fRec2[2] + fSlow10 * fRec2[1]);
			fRec1[0] = fSlow19 * (fRec2[2] + (fRec2[0] - 2.0f * fRec2[1])) - fSlow7 * (fSlow5 * fRec1[2] + fSlow3 * fRec1[1]);
			float fTemp21 = fSlow20 * (fRec1[0] - fRec1[2]) * std::max<float>(0.0f, std::min<float>(fConst2 * fTemp0, fSlow1 * (fConst1 - fTemp0) + 1.0f));
			output0[i0] = FAUSTFLOAT(fTemp21);
			output1[i0] = FAUSTFLOAT(fTemp21);
			fVec0[1] = fVec0[0];
			iVec1[1] = iVec1[0];
			iRec0[1] = iRec0[0];
			fRec4[1] = fRec4[0];
			fVec2[1] = fVec2[0];
			IOTA0 = IOTA0 + 1;
			fRec5[1] = fRec5[0];
			fVec4[1] = fVec4[0];
			fRec6[1] = fRec6[0];
			fVec6[1] = fVec6[0];
			fRec7[1] = fRec7[0];
			fVec8[1] = fVec8[0];
			fRec8[1] = fRec8[0];
			fVec10[1] = fVec10[0];
			fRec9[1] = fRec9[0];
			fVec12[1] = fVec12[0];
			fRec3[2] = fRec3[1];
			fRec3[1] = fRec3[0];
			fRec2[2] = fRec2[1];
			fRec2[1] = fRec2[0];
			fRec1[2] = fRec1[1];
			fRec1[1] = fRec1[0];
		}
	}

};

#endif
