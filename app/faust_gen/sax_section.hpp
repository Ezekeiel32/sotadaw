/* ------------------------------------------------------------
name: "sax_section"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn SaxSection -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __SaxSection_H__
#define  __SaxSection_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS SaxSection
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

class SaxSectionSIG0 {
	
  private:
	
	int iVec1[2];
	int iRec2[2];
	
  public:
	
	int getNumInputsSaxSectionSIG0() {
		return 0;
	}
	int getNumOutputsSaxSectionSIG0() {
		return 1;
	}
	
	void instanceInitSaxSectionSIG0(int sample_rate) {
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			iVec1[l1] = 0;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec2[l2] = 0;
		}
	}
	
	void fillSaxSectionSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec1[0] = 1;
			iRec2[0] = (iVec1[1] + iRec2[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec2[0]));
			iVec1[1] = iVec1[0];
			iRec2[1] = iRec2[0];
		}
	}

};

static SaxSectionSIG0* newSaxSectionSIG0() { return (SaxSectionSIG0*)new SaxSectionSIG0(); }
static void deleteSaxSectionSIG0(SaxSectionSIG0* dsp) { delete dsp; }

static float SaxSection_faustpower2_f(float value) {
	return value * value;
}
static float ftbl0SaxSectionSIG0[65536];

class SaxSection : public dsp {
	
 private:
	
	int iVec0[2];
	int fSampleRate;
	float fConst0;
	float fConst2;
	float fConst4;
	float fConst6;
	float fConst8;
	float fConst10;
	float fConst11;
	float fConst12;
	float fRec3[2];
	FAUSTFLOAT fButton0;
	float fVec2[2];
	int iRec4[2];
	float fConst13;
	float fRec5[2];
	float fConst14;
	FAUSTFLOAT fHslider0;
	float fConst15;
	FAUSTFLOAT fHslider1;
	float fConst16;
	float fRec6[2];
	float fVec3[2];
	int IOTA0;
	float fVec4[4096];
	float fConst17;
	float fConst18;
	float fRec7[2];
	float fRec1[3];
	float fRec0[3];
	float fConst19;
	float fConst21;
	float fConst23;
	float fConst25;
	float fRec9[3];
	float fConst26;
	float fConst28;
	float fConst30;
	float fConst32;
	int iRec11[2];
	float fConst33;
	float fConst34;
	float fConst35;
	int iRec12[2];
	FAUSTFLOAT fHslider2;
	float fRec10[3];
	float fConst36;
	float fConst38;
	FAUSTFLOAT fHslider3;
	float fConst39;
	FAUSTFLOAT fHslider4;
	
 public:
	SaxSection() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn SaxSection -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/asr:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "sax_section.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass:license", "MIT-style STK-4.3 license");
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
		m->declare("name", "sax_section");
		m->declare("noises.lib/name", "Faust Noise Generator Library");
		m->declare("noises.lib/version", "1.4.0");
		m->declare("oscillators.lib/lf_sawpos:author", "Bart Brouns, revised by Stéphane Letz");
		m->declare("oscillators.lib/lf_sawpos:licence", "STK-4.3");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
		m->declare("oscillators.lib/saw2ptr:author", "Julius O. Smith III");
		m->declare("oscillators.lib/saw2ptr:license", "STK-4.3");
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
		SaxSectionSIG0* sig0 = newSaxSectionSIG0();
		sig0->instanceInitSaxSectionSIG0(sample_rate);
		sig0->fillSaxSectionSIG0(65536, ftbl0SaxSectionSIG0);
		deleteSaxSectionSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		float fConst1 = std::tan(3298.6724f / fConst0);
		fConst2 = 2.0f * (1.0f - 1.0f / SaxSection_faustpower2_f(fConst1));
		float fConst3 = 1.0f / fConst1;
		fConst4 = (fConst3 + -0.45454547f) / fConst1 + 1.0f;
		float fConst5 = (fConst3 + 0.45454547f) / fConst1 + 1.0f;
		fConst6 = 1.0f / fConst5;
		float fConst7 = std::tan(8482.3f / fConst0);
		fConst8 = 2.0f * (1.0f - 1.0f / SaxSection_faustpower2_f(fConst7));
		float fConst9 = 1.0f / fConst7;
		fConst10 = (fConst9 + -1.4142135f) / fConst7 + 1.0f;
		fConst11 = 1.0f / ((fConst9 + 1.4142135f) / fConst7 + 1.0f);
		fConst12 = 5.4f / fConst0;
		fConst13 = 1.0f / std::max<float>(1.0f, 0.1f * fConst0);
		fConst14 = 1.0f / std::max<float>(1.0f, 0.28f * fConst0);
		fConst15 = 1.0f / std::max<float>(1.0f, 0.06f * fConst0);
		fConst16 = 1.0f / fConst0;
		fConst17 = 0.5f * fConst0;
		fConst18 = 0.055f * fConst0;
		fConst19 = 1.3f / (fConst1 * fConst5);
		float fConst20 = std::tan(7225.663f / fConst0);
		fConst21 = 2.0f * (1.0f - 1.0f / SaxSection_faustpower2_f(fConst20));
		float fConst22 = 1.0f / fConst20;
		fConst23 = (fConst22 + -0.2857143f) / fConst20 + 1.0f;
		float fConst24 = (fConst22 + 0.2857143f) / fConst20 + 1.0f;
		fConst25 = 1.0f / fConst24;
		fConst26 = 0.5f / (fConst20 * fConst24);
		float fConst27 = std::tan(6911.504f / fConst0);
		fConst28 = 2.0f * (1.0f - 1.0f / SaxSection_faustpower2_f(fConst27));
		float fConst29 = 1.0f / fConst27;
		fConst30 = (fConst29 + -0.5f) / fConst27 + 1.0f;
		float fConst31 = (fConst29 + 0.5f) / fConst27 + 1.0f;
		fConst32 = 1.0f / fConst31;
		fConst33 = std::max<float>(1.0f, 0.02f * fConst0);
		fConst34 = 1.0f / fConst33;
		fConst35 = 1.0f / std::max<float>(1.0f, 0.25f * fConst0);
		fConst36 = 1.0f / (fConst27 * fConst31);
		float fConst37 = std::max<float>(1.0f, 0.12f * fConst0);
		fConst38 = 1.0f / fConst37;
		fConst39 = 0.2f / fConst37;
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(0.018f);
		fHslider1 = FAUSTFLOAT(2.2e+02f);
		fHslider2 = FAUSTFLOAT(0.05f);
		fHslider3 = FAUSTFLOAT(0.03f);
		fHslider4 = FAUSTFLOAT(0.6f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			iVec0[l0] = 0;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			fRec3[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			fVec2[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			iRec4[l5] = 0;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			fRec5[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			fRec6[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			fVec3[l8] = 0.0f;
		}
		IOTA0 = 0;
		for (int l9 = 0; l9 < 4096; l9 = l9 + 1) {
			fVec4[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 2; l10 = l10 + 1) {
			fRec7[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 3; l11 = l11 + 1) {
			fRec1[l11] = 0.0f;
		}
		for (int l12 = 0; l12 < 3; l12 = l12 + 1) {
			fRec0[l12] = 0.0f;
		}
		for (int l13 = 0; l13 < 3; l13 = l13 + 1) {
			fRec9[l13] = 0.0f;
		}
		for (int l14 = 0; l14 < 2; l14 = l14 + 1) {
			iRec11[l14] = 0;
		}
		for (int l15 = 0; l15 < 2; l15 = l15 + 1) {
			iRec12[l15] = 0;
		}
		for (int l16 = 0; l16 < 3; l16 = l16 + 1) {
			fRec10[l16] = 0.0f;
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
	
	virtual SaxSection* clone() {
		return new SaxSection();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("sax_section");
		ui_interface->addHorizontalSlider("attack", &fHslider3, FAUSTFLOAT(0.03f), FAUSTFLOAT(0.005f), FAUSTFLOAT(0.3f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("breath", &fHslider2, FAUSTFLOAT(0.05f), FAUSTFLOAT(0.0f), FAUSTFLOAT(0.2f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("freq", &fHslider1, FAUSTFLOAT(2.2e+02f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(4e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider4, FAUSTFLOAT(0.6f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("vibrato", &fHslider0, FAUSTFLOAT(0.018f), FAUSTFLOAT(0.0f), FAUSTFLOAT(0.05f), FAUSTFLOAT(0.0001f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fButton0);
		int iSlow1 = fSlow0 == 0.0f;
		float fSlow2 = float(fHslider0);
		float fSlow3 = float(fHslider1);
		float fSlow4 = 0.5f * fSlow3;
		float fSlow5 = 4.656613e-10f * float(fHslider2);
		float fSlow6 = std::max<float>(1.0f, fConst0 * float(fHslider3));
		float fSlow7 = 1.0f / fSlow6;
		float fSlow8 = 0.509f * float(fHslider4);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			int iTemp0 = 1 - iVec0[1];
			float fTemp1 = ((iTemp0) ? 0.0f : fConst12 + fRec3[1]);
			fRec3[0] = fTemp1 - std::floor(fTemp1);
			fVec2[0] = fSlow0;
			iRec4[0] = iSlow1 * (iRec4[1] + 1);
			float fTemp2 = float(iRec4[0]);
			fRec5[0] = fSlow0 + fRec5[1] * float(fVec2[1] >= fSlow0);
			float fTemp3 = (0.056f * std::max<float>(0.0f, std::min<float>(fConst15 * fRec5[0], 1.0f) - fConst15 * fTemp2) + 0.944f) * (fSlow2 * std::max<float>(0.0f, std::min<float>(fConst14 * fRec5[0], 1.0f) - fConst13 * fTemp2) * ftbl0SaxSectionSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec3[0]), 65535))] + 1.0f);
			float fTemp4 = std::max<float>(fSlow4 * fTemp3, 23.44895f);
			float fTemp5 = std::max<float>(2e+01f, std::fabs(fTemp4));
			float fTemp6 = ((iTemp0) ? 0.0f : fRec6[1] + fConst16 * fTemp5);
			fRec6[0] = fTemp6 - std::floor(fTemp6);
			float fTemp7 = SaxSection_faustpower2_f(2.0f * fRec6[0] + -1.0f);
			fVec3[0] = fTemp7;
			float fTemp8 = float(iVec0[1]) * (fTemp7 - fVec3[1]) / fTemp5;
			fVec4[IOTA0 & 4095] = fTemp8;
			float fTemp9 = std::max<float>(0.0f, std::min<float>(2047.0f, fConst17 / fTemp4));
			int iTemp10 = int(fTemp9);
			float fTemp11 = std::floor(fTemp9);
			float fTemp12 = std::max<float>(1.1920929e-07f, std::fabs(fSlow3 * fTemp3));
			float fTemp13 = fRec7[1] + fConst16 * fTemp12;
			float fTemp14 = fTemp13 + -1.0f;
			int iTemp15 = fTemp14 < 0.0f;
			fRec7[0] = ((iTemp15) ? fTemp13 : fTemp14);
			float fRec8 = ((iTemp15) ? fTemp13 : fTemp13 + fTemp14 * (1.0f - fConst0 / fTemp12));
			fRec1[0] = 2.0f * fRec8 + fConst18 * (fTemp8 - fVec4[(IOTA0 - iTemp10) & 4095] * (fTemp11 + (1.0f - fTemp9)) - (fTemp9 - fTemp11) * fVec4[(IOTA0 - (iTemp10 + 1)) & 4095]) + (-1.0f - fConst11 * (fConst10 * fRec1[2] + fConst8 * fRec1[1]));
			float fTemp16 = fConst11 * (fRec1[2] + fRec1[0] + 2.0f * fRec1[1]);
			fRec0[0] = fTemp16 - fConst6 * (fConst4 * fRec0[2] + fConst2 * fRec0[1]);
			fRec9[0] = fTemp16 - fConst25 * (fConst23 * fRec9[2] + fConst21 * fRec9[1]);
			iRec11[0] = (iRec11[1] + (iRec11[1] > 0)) * (fSlow0 <= fVec2[1]) + (fSlow0 > fVec2[1]);
			float fTemp17 = float(iRec11[0]);
			iRec12[0] = 1103515245 * iRec12[1] + 12345;
			fRec10[0] = fSlow5 * float(iRec12[0]) * std::max<float>(0.0f, std::min<float>(fConst34 * fTemp17, fConst35 * (fConst33 - fTemp17) + 1.0f)) - fConst32 * (fConst30 * fRec10[2] + fConst28 * fRec10[1]);
			float fTemp18 = fSlow8 * std::max<float>(0.0f, std::min<float>(fSlow7 * fRec5[0], std::max<float>(fConst39 * (fSlow6 - fRec5[0]) + 1.0f, 0.8f)) * (1.0f - fConst38 * fTemp2)) * (fConst36 * (fRec10[0] - fRec10[2]) + 0.476f * (fConst26 * (fRec9[0] - fRec9[2]) + fTemp16 + fConst19 * (fRec0[0] - fRec0[2])));
			output0[i0] = FAUSTFLOAT(fTemp18);
			output1[i0] = FAUSTFLOAT(fTemp18);
			iVec0[1] = iVec0[0];
			fRec3[1] = fRec3[0];
			fVec2[1] = fVec2[0];
			iRec4[1] = iRec4[0];
			fRec5[1] = fRec5[0];
			fRec6[1] = fRec6[0];
			fVec3[1] = fVec3[0];
			IOTA0 = IOTA0 + 1;
			fRec7[1] = fRec7[0];
			fRec1[2] = fRec1[1];
			fRec1[1] = fRec1[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
			fRec9[2] = fRec9[1];
			fRec9[1] = fRec9[0];
			iRec11[1] = iRec11[0];
			iRec12[1] = iRec12[0];
			fRec10[2] = fRec10[1];
			fRec10[1] = fRec10[0];
		}
	}

};

#endif
